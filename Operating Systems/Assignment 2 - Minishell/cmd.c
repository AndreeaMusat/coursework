/**
 * Operating Systems 2013-2017 - Assignment 2
 *
 * Andreea Musat, 333CA
 *
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <fcntl.h>
#include <unistd.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cmd.h"
#include "utils.h"

#define READ		0
#define WRITE		1


static int do_redirect(int filedes, const char *filename, int io_flags)
{
	int rc;
	int fd;
	int oflag;

	/* Redirect filedes into fd representing filename */
	if (filedes == STDIN_FILENO) {

		fd = open(filename, O_RDONLY);

	} else if (filedes == STDOUT_FILENO || filedes == STDERR_FILENO) {

		if (io_flags == IO_REGULAR) {
			oflag = O_WRONLY | O_CREAT | O_TRUNC;
			fd = open(filename, oflag, 0644);
		}

		else if (io_flags == IO_OUT_APPEND ||
			     io_flags == IO_ERR_APPEND) {
			oflag =  O_WRONLY | O_CREAT | O_APPEND;
			fd = open(filename, oflag, 0644);
		}
	}

	DIE(fd < 0, "openFileRedirect");

	/* duplicate the file descriptor fd to filedes */
	rc = dup2(fd, filedes);

	return rc;
}

/**
 * Internal change-directory command.
 */
static bool shell_cd(word_t *dir)
{
	int res;
	char *dir_name;

	if (dir == NULL)
		dir_name = getenv("HOME");
	else
		dir_name = get_word(dir);

	res = chdir(dir_name);
	if (res == -1) {
		printf("mini-shell: cd: %s: No such file or directory\n",
			dir->string);
		return res;
	}

	return 0;
}

/**
 * Internal exit/quit command.
 */
static int shell_exit(void)
{
	return SHELL_EXIT;
}

/**
 * Parse a simple command (internal, environment variable assignment,
 * external command).
 */
static int parse_simple(simple_command_t *s, int level, command_t *father)
{
	int res, cond, size, status, fd, oflag;
	bool out_and_err_redirect = false;
	pid_t pid;

	const char *command_name = NULL;
	const char *variable_name = NULL;
	const char *value = NULL;
	const char *filename_in = NULL;
	const char *filename_out = NULL;
	const char *filename_err = NULL;

	char **args;

	/* sanity checks */
	if (s == NULL || s->verb == NULL)
		return -1;

	/* if builtin command, execute the command */
	command_name = s->verb->string;

	// printf("parsing simple command = %s\n", command_name);

	cond = strcmp(command_name, "cd") == 0 ? 1 : 0;
	if (cond) {
		if (s->out != NULL) {
			filename_out = s->out->string;
			oflag = O_WRONLY | O_CREAT | O_TRUNC;
			fd = open(filename_out, oflag, 0600);
			DIE(fd < 0, "openFileCd");
			close(fd);
		}
		res = shell_cd(s->params);
		return res;
	}

	cond = strcmp(command_name, "exit") == 0 ? 1 : 0;
	cond |= (strcmp(command_name, "quit") == 0 ? 1 : 0);
	if (cond) {
		res = shell_exit();
		return res;
	}

	/* variable assignment => "name" "=" "value" */
	if (s->verb->next_part != NULL) {
		variable_name = s->verb->string;

		/* if there is a value in the assignment */
		if (s->verb->next_part->next_part != NULL)
			value = s->verb->next_part->next_part->string;
		else
			return -1;

		/* execute the assignment */
		if (value != NULL) {
			res = setenv(variable_name, value, 1); /* replace */
			DIE(res != 0, "setEnv");

			return res;
		}
	}

	/* if external command, fork new process */
	pid = fork();

	/* error forking */
	if (pid == -1)
		DIE(1, "parseSimpleFork");

	/* child process */
	if (pid == 0) {

		/* in, out, err point to the names of the redirections */
		if (s->out != NULL && s->err != NULL)
			out_and_err_redirect = true;

		if (s->in != NULL) {
			filename_in = get_word(s->in);
			res = do_redirect(STDIN_FILENO, filename_in,
				s->io_flags);
			DIE(res < 0, "redirectStdin");
		}
		/* (truncate) redirect the error */
		if (s->err != NULL) {
			filename_err = get_word(s->err);

			if (!out_and_err_redirect)
				res = do_redirect(STDERR_FILENO,
					filename_err, s->io_flags);
			else
				res = do_redirect(STDERR_FILENO,
					filename_err, s->io_flags);

			DIE(res < 0, "redirectStderr");
		}
		if (s->out != NULL) {
			filename_out = get_word(s->out);

			if (!out_and_err_redirect)
				res = do_redirect(STDOUT_FILENO,
					filename_out, s->io_flags);
			else
				res = do_redirect(STDOUT_FILENO,
					filename_out, IO_OUT_APPEND);

			DIE(res < 0, "redirectStdout");
		}

		command_name = get_word(s->verb);
		args = get_argv(s, &size);

		res = execvp(command_name, args);
		if (res == -1)
			fprintf(stderr, "Execution failed for '%s'\n", command_name);

		exit(EXIT_FAILURE);
	}

	if (pid != -1 && pid != 0) {
		/* only the parent gets here; wait for child */
		res = waitpid(pid, &status, 0);
		DIE(res < 0, "WaitPid");


		/* return the actual exit status */
		if (WIFEXITED(status))
			return WEXITSTATUS(status);
	}

	return 0;
}

/**
 * Process two commands in parallel, by creating two children.
 */
static bool do_in_parallel(command_t *cmd1, command_t *cmd2,
	int level, command_t *father)
{
	int status, res, wait;
	pid_t pid;

	pid = fork();
	if (pid == -1)
		DIE(1, "fork");

	/* child */
	if (pid == 0) {
		/* execute first command */
		res = parse_command(cmd1, level + 1, father);
		exit(res);
	}

	if (pid > 0) {
		/* execute second command */
		res = parse_command(cmd2, level + 1, father);

		/* then wait for the child to finish */
		wait = waitpid(pid, &status, 0);
		DIE(wait < 0, "waitpid");

		return res;
	}

	return EXIT_SUCCESS;
}


/**
 * Run commands by creating an anonymous pipe (cmd1 | cmd2)
 */
static bool do_on_pipe(command_t *cmd1, command_t *cmd2, int level,
		command_t *father)
{
	int pipe_fd[2]; /* child - child */
	int res, rc, result;
	int status1, status2;
	pid_t pid1, pid2;

	res = pipe(pipe_fd);
	DIE(res < 0, "pipe");

	pid1 = fork();
	switch (pid1) {

	/* error forking */
	case -1:
		return EXIT_FAILURE;
	break;

	/* child 1 */
	case 0:

		/* create second process */
		pid2 = fork();

		switch (pid2) {
		/* error forking */
		case -1:
			return EXIT_FAILURE;
		break;

		/* child 2 */
		case 0:
			/* close reading end of pipe_fd */
			close(pipe_fd[0]);

			/* redirect stdout to pipe_fd[1] */
			rc = dup2(pipe_fd[1], STDOUT_FILENO);
			DIE(rc < 0, "dup2");

			/* execute command */
			result = parse_command(cmd1,
				level + 1, father);

			/* exit process */
			exit(result);

		break;

		/* parent of child 2 = child 1 */
		default:

			/* close writing end of pipe 1 */
			close(pipe_fd[1]);

			/* redirect input to pipe_fd[0] */
			rc = dup2(pipe_fd[0], STDIN_FILENO);
			DIE(rc < 0, "dup2");

			/* get the result of the command */
			result = parse_command(cmd2,
				level + 1, father);

			/* wait for child 2 */
			waitpid(pid2, &status2, 0);

			/* exit process */
			if (WEXITSTATUS(status1) == 0)
				exit(result);
			else
				return EXIT_FAILURE;

		break;
		}
	break;

	default:
		/* close both ends of pipe 1 */
		close(pipe_fd[0]);
		close(pipe_fd[1]);

		/* wait for child 1 */
		waitpid(pid1, &status1, 0);

		if (WEXITSTATUS(status1) == 0)
			return true;

		return false;

	break;
	}
}



/**
 * Parse and execute a command.
 */
int parse_command(command_t *c, int level, command_t *father)
{
	int res1, res2;

	/* sanity checks */
	if (c == NULL)
		return 0;

	if (c->op == OP_NONE) {
		/* execute a simple command */
		res1 = parse_simple(c->scmd, level + 1, c);
		return res1;
	}

	switch (c->op) {
	case OP_SEQUENTIAL:
		/* execute the commands one after the other */
		res1 = parse_command(c->cmd1, level + 1, c);
		res2 = parse_command(c->cmd2, level + 1, c);
		return (res1 > res2) ? res1 : res2;

	case OP_PARALLEL:
		/* execute the commands simultaneously */
		res1 = do_in_parallel(c->cmd1, c->cmd2, level + 1, c);
		if (res1 == false)
			return EXIT_FAILURE;
		else
			return EXIT_SUCCESS;

	case OP_CONDITIONAL_NZERO:
		/* execute the 2nd command only if the 1st returns non 0 */
		res1 = parse_command(c->cmd1, level + 1, c);
		if (res1 != 0)
			return parse_command(c->cmd2, level + 1, c);
		else
			return res1;

	case OP_CONDITIONAL_ZERO:
		/* execute 2nd command only if the first returns 0 */
		res1 = parse_command(c->cmd1, level + 1, c);
		if (res1 == 0)
			return parse_command(c->cmd2, level + 1, c);
		else
			return res1;

	case OP_PIPE:
		/* redirect output of the 1st command to the input of the 2nd */
		res1 = do_on_pipe(c->cmd1, c->cmd2, level + 1, c);
		if (res1 == true)
			return EXIT_SUCCESS;
		else
			return EXIT_FAILURE;

	default:
		return SHELL_EXIT;
	}

	return 0;
}

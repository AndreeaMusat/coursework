import java.util.*;
import java.util.concurrent.*;
import java.io.*;

public class Main {

	static int queueSize;
	static int noOfEventsPerFile;
	static int noOfFiles;
	static int noOfProcessors;
	static int max;
	
	static List<Integer> primeRes = Collections.synchronizedList(new ArrayList<Integer>());
	static List<Integer> fiboRes = Collections.synchronizedList(new ArrayList<Integer>());
	static List<Integer> factRes = Collections.synchronizedList(new ArrayList<Integer>());
	static List<Integer> sqrtRes = Collections.synchronizedList(new ArrayList<Integer>());
	
	static LinkedBlockingQueue<Query> queue = new LinkedBlockingQueue<Query>();

	static ExecutorService readExecutor;
	static ExecutorService queryExecutor;
	
	static File primeFile = new File("PRIME.out");
	static File fiboFile = new File("FIB.out");
	static File factFile = new File("FACT.out");
	static File sqrtFile = new File("SQUARE.out");
	
	public static void main(String[] args) {
		
		long t1 = System.currentTimeMillis();
		
		if (args.length < 3) {
			System.err.println("Wrong command line arguments.. Exiting..");
			System.exit(1);
		}
		
		try {
			queueSize = Integer.parseInt(args[0]);
			noOfEventsPerFile = Integer.parseInt(args[1]);
			noOfFiles = args.length - 2;
			noOfProcessors =  Runtime.getRuntime().availableProcessors();
			max = (int)1e9;
		} catch (NumberFormatException e) {
			System.exit(1);
		}
		
		readExecutor = Executors.newFixedThreadPool(noOfProcessors);
		queryExecutor = Functions.newFixedThreadPoolWithQueueSize(noOfProcessors, queueSize);
		
		for (int i = 2; i < args.length; i++) 
			readExecutor.submit(new ReadFromFile(args[i]));	
		
		readExecutor.shutdown();
		
		try {
			  readExecutor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		} catch (InterruptedException e) {}
		
		while (!queue.isEmpty()) {
			queryExecutor.submit(queue.poll());
		}
		queryExecutor.shutdown();
		
		try {
			queryExecutor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		} catch (InterruptedException e) {}
		
		Collections.sort(primeRes);
		Collections.sort(factRes);
		Collections.sort(fiboRes);
		Collections.sort(sqrtRes);
		
		Functions.writeArrayListToFile(primeFile, primeRes);
		Functions.writeArrayListToFile(factFile, factRes);
		Functions.writeArrayListToFile(fiboFile, fiboRes);
		Functions.writeArrayListToFile(sqrtFile, sqrtRes);
		
		long t2 = System.currentTimeMillis();
		double dt = (t2 - t1) / 1000.0;
		System.out.println("ELAPSED TIME: " + dt);
	}
}


class Functions {
	static ExecutorService newFixedThreadPoolWithQueueSize(int nThreads, int queueSize) {
	    return new 
	    		ThreadPoolExecutor(nThreads, nThreads,
	                              5000L, TimeUnit.MILLISECONDS,
	                             new ArrayBlockingQueue<Runnable>(queueSize, true), 
	                             new ThreadPoolExecutor.CallerRunsPolicy());
	}
	
	static void writeArrayListToFile(File file, List<Integer> list) {
		FileWriter fw = null;
		BufferedWriter bw = null;
		try {
			if (!file.exists())
				file.createNewFile();
			
			fw = new FileWriter(file.getAbsoluteFile());
			bw = new BufferedWriter(fw);
			
			synchronized(list) {
				Iterator<Integer> i = list.iterator();
				while (i.hasNext())
					bw.write(i.next().toString() + "\n");
			}  	
		
			bw.close();
			fw.close();
			
		} catch (Exception e) {}
		
	}
	
	static ArrayList<Integer> generateFibo(int max) {
		ArrayList<Integer> fibo = new ArrayList<Integer>();
		
		fibo.add(0);
		fibo.add(1);
		int res = 1;
		while (res <= max) {
			fibo.add(res);
			res = fibo.get(fibo.size() - 1) +
			  fibo.get(fibo.size() - 2);
		}
		
		return fibo;
	}

	static ArrayList<Integer> generateFact(int max) {
		ArrayList<Integer> fact = new ArrayList<Integer>();
		
		fact.add(1);
		int res = 1;
		for (int i = 1; ; i++)
			if ((res = res * i) <= max)
				fact.add(res);
			else break;
		
		return fact;
	}
}

enum eventType {
	PRIME, FACT, SQUARE, FIB;
	
	static eventType getType(String s) {
		if (s.equals("PRIME"))
			return PRIME;
		else if (s.equals("FACT"))
			return FACT;
		else if (s.equals("SQUARE"))
			return SQUARE;
		return FIB;
	}
}
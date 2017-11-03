OBJ_LIST = hash.obj
CFLAGS = /nologo /W3 /EHsc /Za /DWIN /D_CRT_SECURE_NO_WARNINGS
DLLNAMES = hash.dll

build: tema1

tema1: tema1.obj list.obj hashtable.obj
	cl $(CFLAGS) tema1.obj list.obj hashtable.obj hash.lib /Fetema1

tema1.obj: tema1.c
	cl $(CFLAGS) /c tema1.c /Fotema1.obj

list.obj: list.c
	cl $(CFLAGS) /c list.c /Folist.obj

hashtable.obj: hashtable.c
	cl $(CFLAGS) /c hashtable.c  /Fohashtable.obj

hash.dll : $(OBJ_LIST)
	link /dll /out:$@ $**

hash.obj :
	cl $(CFLAGS) /c hash.c

clean: 
	del tema1 *.obj 

dll_clean : 
	del $(DLLNAMES)

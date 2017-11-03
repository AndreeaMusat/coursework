import java.util.*;

public abstract class Query implements Runnable {
	int N;
	eventType type;
	
	Query(int N, eventType type) {
		this.N = N;
		this.type = type;
	}
}

class PrimeQuery extends Query {
	
	PrimeQuery(int N, eventType type) {
		super(N, type);
	}
	
	static boolean isPrime(int n) {
	    
		if(n < 2) return false;
	    
		if(n == 2 || n == 3) return true;
	    
		if(n%2 == 0 || n%3 == 0) return false;
	    
		int sqrtN = (int)Math.sqrt(n)+1;
	    for(int i = 6; i <= sqrtN; i += 6) {
	        if(n % (i-1) == 0 || n % (i+1) == 0) return false;
	    }
	    return true;
	}
	
	@Override
	public void run() {
		for (int i = N; i >= 2; i--)
			if (isPrime(i)) {
				Main.primeRes.add(i);
				return;
			}
		
		return;
	}
}


class FiboQuery extends Query {

	static ArrayList<Integer> fibo = Functions.generateFibo(Main.max);
	
	FiboQuery(int N, eventType type) {
		super(N, type);
	}
	
	@Override
	public void run() {
		for (int i = 0; i < fibo.size() - 1; i++)
			if (fibo.get(i) <= N && fibo.get(i + 1) > N) {
				Main.fiboRes.add(i);
				return;
			}
		
		return;
	}
}

class FactQuery extends Query {
	
	static ArrayList<Integer> fact = Functions.generateFact(Main.max);
	
	FactQuery(int N, eventType type) {
		super(N, type);
	}
	
	@Override
	public void run() {
		for (int i = 0; i < fact.size() - 1; i++)
			if (fact.get(i) <= N && fact.get(i + 1) > N) {
				Main.factRes.add(i);
				return;
			}
		
		return ;
	}
}

class SqrtQuery extends Query {
	
	SqrtQuery(int N, eventType type) {
		super(N, type);
	}
	
	@Override 
	public void run() {
		Main.sqrtRes.add((int)Math.floor(Math.sqrt(N)));
	}
}
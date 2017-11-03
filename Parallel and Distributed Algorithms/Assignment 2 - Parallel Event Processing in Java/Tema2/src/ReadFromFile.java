import java.io.*;

public class ReadFromFile implements Runnable {
	String fileName;
	
	public ReadFromFile(String fileName) {
		this.fileName = fileName;
	}
	
	@Override 
	public void run() {
		File fin = new File(fileName);
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(fin));
			
			String line = null;
			String data[] = new String[3];
			
			while ((line = br.readLine()) != null) {
				
				data = line.split(",");
				
				int time = Integer.parseInt(data[0]);
				eventType type = eventType.getType(data[1]);
				int N = Integer.parseInt(data[2]);
				
				Thread.sleep(time);
			
				switch(type) {
				case SQUARE: 
					Main.queue.add(new SqrtQuery(N, eventType.SQUARE));
					break;
				case PRIME:
					Main.queue.add(new PrimeQuery(N, eventType.PRIME));
					break;
				case FIB:
					Main.queue.add(new FiboQuery(N, eventType.FIB));
					break;
				case FACT:
					Main.queue.add(new FactQuery(N, eventType.FACT));
					break;
				}	
			}
			
			br.close();
		} catch (Exception e) {	} 
	}
}
import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

int numChannels = 16;  // Number of MIDI channels
int[] channelColors;   // Colors for each channel
Particle[] particles;  // Array of particles
float bpm = 120;  // init BPM
float lastBeatTime = 0;
float beatInterval;  // time interval between beats

void setup() {
  size(800, 600);
  frameRate(60);

  // Initialize OSC
  oscP5 = new OscP5(this, 57120);  // Listening port

  // Initialize colors for each MIDI channel
  channelColors = new int[numChannels];
  for (int i = 0; i < numChannels; i++) {
    channelColors[i] = color(random(255), random(255), random(255), 150);  // Semi-transparent
  }

  // Initialize particle array
  particles = new Particle[256];
  for (int i = 0; i < particles.length; i++) {
    particles[i] = new Particle();
  }
}

void draw() {
  // Calculate beat interval from BPM
  beatInterval = 60.0 / bpm * 1000; // Convert BPM to milliseconds

  // Dynamic background
  fill(0, 10);
  rect(0, 0, width, height);

  // Update and display particles
  for (Particle p : particles) {
    if (p.isActive()) {
      p.update();
      p.display();
    }
  }

  // Check for beat
  if (millis() - lastBeatTime > beatInterval) {
    lastBeatTime = millis();
    onBeat();  // Function called on every beat
  }
}


void oscEvent(OscMessage theOscMessage) {
  String addrPattern = theOscMessage.addrPattern();
  
  println("OSC Event Triggered with pattern: " + addrPattern);

  if (addrPattern.startsWith("/midi/")) {
    try {
      int channel = Integer.parseInt(addrPattern.substring(6));
      int status = theOscMessage.get(0).intValue(); // MIDI status byte
      int note = theOscMessage.get(1).intValue();   // MIDI note number
      int velocity = theOscMessage.get(2).intValue(); // MIDI velocity

      println("Received OSC: Channel " + channel + ", Status " + status + ", Note " + note + ", Velocity " + velocity); // Debug print

      // Check if it's a Note On message and note is in range
      if (status == 144 && note >= 0 && note < particles.length) {
        particles[note].activate(channelColors[channel - 1], velocity);
      }
    } catch (NumberFormatException e) {
      println("Error parsing OSC message: " + addrPattern);
    }
  } else {
    println("Unknown OSC message: " + addrPattern); // print unknown patterns
  }

  if (addrPattern.equals("/tempo")) {
    bpm = theOscMessage.get(0).floatValue();
    println("Received BPM: " + bpm);
  }
}

void onBeat() {
  // Logic to execute on every beat
  for (int i = 0; i < particles.length; i++) {
    if (!particles[i].isActive()) {
      particles[i].activate(channelColors[int(random(numChannels))], random(128, 255));
      break; // Activate one particle per beat
    }
  }
}

// Particle class
class Particle {
  PVector position;
  PVector velocity;
  int col;
  float alpha;
  boolean active;

  Particle() {
    position = new PVector(width / 2, height / 2);
    velocity = new PVector();
    col = color(255);
    alpha = 0;
    active = false;
  }

  void activate(int newCol, float velocityFactor) {
    position.set(random(width), random(height));
    velocity.set(random(-2, 2), random(-2, 2));
    col = newCol;
    alpha = map(velocityFactor, 0, 127, 50, 255); // alpha range
    active = true;
  }

  void update() {
    // movement logic for smoother trajectories
    velocity.add(PVector.random2D().mult(0.5)); // random acceleration
    velocity.limit(5); // Limit speed for smoother motion
    position.add(velocity);

    alpha *= 0.98; // Slower fade out
    if (alpha < 20) active = false; // Lower threshold for deactivation
  }

  void display() {
    // Larger size...
    float size = 100 + alpha / 10;
    fill(col, alpha);
    noStroke();
    ellipse(position.x, position.y, size, size);
  }

  void interact(Particle[] others) {
    // Particle interaction logic
    for (Particle other : others) {
      float distance = dist(position.x, position.y, other.position.x, other.position.y);
      if (distance < 50 && distance > 0) {
        PVector repel = PVector.sub(position, other.position);
        repel.div(distance * distance);
        position.add(repel);
      }
    }
  }

  boolean isActive() {
    return active;
  }
}

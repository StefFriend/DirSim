import oscP5.*;
import netP5.*;

OscP5 oscP5;
float bpm = 120; // Default BPM
int numChannels = 16; // Number of MIDI channels
int[] channelColors; // Colors for each channel
Particle[] particles; // Array of particles

void setup() {
  size(800, 600);
  frameRate(60);

  // Initialize OSC
  oscP5 = new OscP5(this, 57120);

  // Initialize colors for each MIDI channel
  channelColors = new int[numChannels];
  for (int i = 0; i < numChannels; i++) {
    channelColors[i] = color(random(255), random(255), random(255), 150); // Semi-transparent
  }

  // Initialize particle array
  particles = new Particle[256];
  for (int i = 0; i < particles.length; i++) {
    particles[i] = new Particle();
  }
}

void draw() {
  background(0);

  // Update and display particles
  for (Particle p : particles) {
    p.update();
    p.display();
  }
}

void oscEvent(OscMessage theOscMessage) {
  // ... [OSC message handling as before] ...
}

class Particle {
  PVector position;
  PVector velocity;
  int col;
  float alpha;
  boolean active;
  float size;
  ArrayList<PVector> history; // To store the trail positions

  Particle() {
    position = new PVector(random(width), random(height));
    velocity = new PVector(random(-1, 1), random(-1, 1));
    col = color(255);
    alpha = 0;
    active = false;
    size = 5; // Initial size
    history = new ArrayList<PVector>();
  }

  void activate(int newCol, float velocityFactor) {
    position.set(random(width), random(height));
    velocity.set(random(-2, 2), random(-2, 2));
    col = newCol;
    alpha = map(velocityFactor, 0, 127, 50, 255); // Map MIDI velocity to alpha range
    active = true;
    history.clear(); // Clear the history for new activation
  }

  void update() {
    if (active) {
      position.add(velocity);
      alpha *= 0.96; // Fade out
      size += 0.1; // Increase size over time
      history.add(position.copy());
      if (history.size() > 10) {
        history.remove(0); // Limit the trail length
      }
      if (alpha < 2) {
        active = false; // Deactivate if faded out
      }
    }
  }

  void display() {
    if (active) {
      noFill();
      beginShape();
      for (PVector p : history) {
        vertex(p.x, p.y);
      }
      endShape();

      fill(col, alpha);
      noStroke();
      ellipse(position.x, position.y, size, size); // Draw particle with current size
    }
  }
}

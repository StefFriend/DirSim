// Wave class
class Wave {
  PVector position;    // Current position
  PVector velocity;    // Velocity of the particle
  PVector acceleration;  // Acceleration to influence movement
  float lifespan;      // Lifespan of the particle
  float waveFrequency; // Frequency of wave oscillation
  float waveAmplitude; // Amplitude of wave oscillation
  float waveOffset;    // Phase offset for wave movement
  ArrayList<PVector> trail;  // To store the previous positions (for the tail)
  int maxTrailLength;  // Maximum length of the tail
  
  int activity;
  
  Wave(PVector pos, int velocityFactor, int note) {
    position = pos.copy();
    velocity = new PVector(random(-4,4), 0);  // Horizontal velocity
    acceleration = new PVector(0, 0.8);  // Gravity-like acceleration (slight downward)
    lifespan = 255;  // Lifespan starts at 255 (fully opaque)
    trail = new ArrayList<PVector>();  // Initialize empty trail
    maxTrailLength = 30;  // Define maximum trail length
    this.activity = velocityFactor; 

    // Wave properties
    waveFrequency = 0.2;  // Random wave frequency
    waveAmplitude = 10;    // Random wave amplitude
    waveOffset = random(TWO_PI);        // Random wave offset (phase)
  }
  
  // Apply repelling force based on distance to other waves
  void applyRepelForce() {
    for (Wave other : waves) {
      if (other != this) {
        float d = dist(position.x, position.y, other.position.x, other.position.y);
        if (d < repelRadius && d > 0) {
          PVector repelDir = PVector.sub(position, other.position);
          repelDir.normalize();  // Get direction
          float strength = repelStrength / d;  // Repel strength weakens with distance
          repelDir.mult(strength);  // Scale force by strength
          acceleration.add(repelDir);  // Apply repel force to acceleration
        }
      }
    }
  }

  void update() {
    // Update trail
    trail.add(position.copy());  // Store current position in the trail
    if (trail.size() > maxTrailLength) {
      trail.remove(0);  // Remove the oldest position if trail is too long
    }
    
    // Apply wave movement to the y-coordinate
    position.y += sin(frameCount * waveFrequency + waveOffset) * waveAmplitude;
    
    // Apply acceleration to velocity
    velocity.add(acceleration);
    
    // Update position with wave movement and velocity
    position.add(velocity);
    
    // Reduce lifespan gradually
    lifespan -=10 ;
    
    // Reset acceleration for the next frame
    acceleration.mult(0);
  }
  
  void display() {
    // Draw the trail
    float alpha = map(this.activity, 0, 127, 0, 255);
    for (int i = 0; i < trail.size(); i++) {
      //float alpha = map(i, 0, trail.size(), 0, 255);  // Trail fading effect
      fill(familyColors[2], alpha);  // Set color with alpha transparency
      float r = map(i, 0, trail.size(), 5, 30);  // Radius gets bigger closer to the particle
      PVector tPos = trail.get(i);
      ellipse(tPos.x, tPos.y, r, r);  // Draw circles at each trail point
    }
    
    // Draw the particle itself
    noStroke();
    fill(familyColors[2], lifespan);  // White particle with fading effect
    ellipse(position.x, position.y, 30, 30);  // Main particle
  }
  
  boolean isDead() {
    return lifespan <= 0;  // Wave is dead when lifespan is below 0
  }
}

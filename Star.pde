// Particle class
class Star {
  PVector position;    // Current position
  PVector velocity;    // Velocity of the particle
  PVector acceleration;  // Acceleration to influence movement
  float lifespan;      // Lifespan of the particle
  ArrayList<PVector> trail;  // To store the previous positions (for the tail)
  int maxTrailLength;  // Maximum length of the trail
  
  Star(PVector pos) {
    position = pos.copy();
    velocity = PVector.random2D();  // Random velocity
    velocity.mult(random(2, 4));    // Random speed
    acceleration = new PVector(0, 0.05);  // Gravity-like acceleration
    lifespan = 255;  // Lifespan starts at 255 (fully opaque)
    trail = new ArrayList<PVector>();  // Initialize empty trail
    maxTrailLength = 20;  // Define maximum trail length
  }
  
  void update() {
    // Update trail
    trail.add(position.copy());  // Store current position in the trail
    if (trail.size() > maxTrailLength) {
      trail.remove(0);  // Remove the oldest position if trail is too long
    }
    
    velocity.add(acceleration);  // Apply acceleration to velocity
    position.add(velocity);      // Update position based on velocity
    
    lifespan -= 20;  // Reduce lifespan gradually
  }
  
  void display() {
    // Draw the trail
    
    for (int i = 0; i < trail.size(); i++) {
      float alpha = map(i, 0, trail.size(), 0, 255);  // Trail fading effect
      float r = map(i, 0, trail.size(), 2, 10);  // Radius gets bigger closer to the star
      PVector tPos = trail.get(i);
      fill(familyColors[3], alpha);  // Set color with alpha transparency
      ellipse(tPos.x, tPos.y, r, r);  // Draw circles at each trail point
    }
    
    // Draw the particle (star) itself
    //noStroke();
    fill(familyColors[3], lifespan);  // Purple star with fading effect
    ellipse(position.x, position.y, 12, 12);  // Main particle (star)
  }
  
  boolean isDead() {
    return lifespan <= 0;  // Particle is dead when lifespan is below 0
  }
}

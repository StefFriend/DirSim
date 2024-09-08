class Particle {
  PVector position;
  PVector velocity;
  int col;
  float alpha;
  boolean active;

  Particle() {
    position = new PVector(-width/2, -height*0.9);
    velocity = new PVector();
    col = color(255);
    alpha = 0;
    active = false;
  }

  void activate(int newCol, float velocityFactor, int note) {
    float positiony = map(note,21,108,-height/2,-height);
    position.set(random(-width/2,width/2), positiony);
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
    if (alpha < 20) active = false; // Lower threshold for desactivation
  }

  void display() {
    // Larger size...
    float size = 30 + alpha / 10;
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

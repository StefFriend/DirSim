// Class to represent a section (Particle)
class Section {
  float innerRowRadius, outerRowRadius;
  float startAngle, endAngle;
  String name;
  color baseColor;  // Particle color
  float activity;
  
  String[] sectionFamilies = {"VIOLIN 1ST", "HARP", "VIOLIN 2ND", "FLUTE",
   "OBOE", "FRENCH HORN", "TRUMPET", "PERCUSSION", "VIOLA", "CLARINET",
   "BASSOON", "TROMBONE", "TUBA", "TIMPANI", "CELLO", "DOUBLE BASS"};
  
  Section(float innerR, float outerR, float startA, float endA, color baseColor) {
    this.innerRowRadius = innerR;
    this.outerRowRadius = outerR;  // Add padding to outer radius
    this.startAngle = startA;
    this.endAngle = endA;
    this.baseColor = baseColor;
    this.activity = 0;
  }
  
  void playNote(int note, int velocity) {
    activity = map(velocity, 0, 127, 0.3, 1);
  }
  
  void noteOff() {
    activity *= 0.5;
  }
  
  void update() {
    activity *= 0.95;
  }
  void display(int number) {
    
    color currentColor = lerpColor(color(200), baseColor, activity);
    fill(currentColor);  // Set fill to the particle color
    
    // Draw the inner arc for the particle
    beginShape();
    for (float a = startAngle; a <= endAngle; a += 0.001) {
      float x = cos(a) * innerRowRadius;
      float y = sin(a) * innerRowRadius;
      vertex(x, y);
    }

    // Draw the outer arc for the particle (in reverse)
    for (float a = endAngle; a >= startAngle; a -= 0.001) {
      float x = cos(a) * outerRowRadius;
      float y = sin(a) * outerRowRadius;
      vertex(x, y);
    }
    endShape(CLOSE);
    
    // Calculate the position to place the number (center of the section)
    float avgRadius = (innerRowRadius + outerRowRadius) / 2;
    float avgAngle = (startAngle + endAngle) / 2;
    float xText = cos(avgAngle) * avgRadius;
    float yText = sin(avgAngle) * avgRadius;
    
    // Draw the number
    fill(0);  // Set fill color to black for the text
    textAlign(CENTER, CENTER);
    textSize(12);
    name = sectionFamilies[number];
    text(name, xText, yText);
  }
  
  boolean isActive() {
    return activity > 0.1;
  }
}

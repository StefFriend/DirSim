import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

float bpm = 132;
float lastBeatTime = 0;
float beatInterval;
float size = 70;

int mainSections = 4;
float innerRadius = 80;
float outerRadius = 350;
float startAngle = PI;  // Start of the arc
float endAngle = 2 * PI;  // End of the arc

int starsPerNote= 20;  // Number of stars to spawn per note
float xStar,yStar;

int wavesPerClick = 1;  // Number of waves to spawn per click
float repelRadius = 100;  // Radius within which waves repel each other
float repelStrength = 3;  // Strength of repelling force

// Particles systems
ArrayList<Section> sections = new ArrayList<Section>();
Particle[] particles;  // Array of particles
ArrayList<Star> stars;  // List to store all stars
ArrayList<Wave> waves;  // List to store all waves

color[] familyColors = {
  #4169E1, // Strings (Royal Blue)
  #228B22, // Woodwinds (Forest Green)
  #DAA520, // Brass (Goldenrod)
  #8B008B  // Percussion and others (Dark Magenta)
};

// Debug variables
boolean debugMode = false;
String lastOscMessage = "No message received yet";

color backgroundColor; // Background color
color conducterColor; // Conducter color
color colSection; // Sections Color

void setup() {
  size(1000, 800);
  surface.setTitle("Dirsim Visual");
  frameRate(60);
  
  oscP5 = new OscP5(this, 57120);
  
  // Set static background color
  backgroundColor = color(51,51,51); // Light grayish-blue
  
  // Create Sections
  createSections();
  waves = new ArrayList<Wave>();  // Initialize wave array
  
  // Initialize particle array
  particles = new Particle[160];
  for (int i = 0; i < particles.length; i++) {
    particles[i] = new Particle();
  }
  stars = new ArrayList<Star>();  // Initialize particle array
  println("Setup completed. Waiting for MIDI messages...");
}

void draw() {
  // Static background
  background(backgroundColor);
  translate(width/2, height*0.9);
  
  beatInterval = 60000 / bpm;

  // Display Orchstra Sections
  for (int i = 0; i < sections.size(); i++) {
    Section s = sections.get(i);
    s.update();
    s.display(i);  // Display section with a number starting from 1
  }
  
  // Update and display circle particles
  for (Particle p : particles) {
    if (p.isActive()) {
      p.update();
      p.display();
    }
  }
  
  // Display and update all particles
  for (int i = stars.size() - 1; i >= 0; i--) {
    Star s = stars.get(i);
    s.update();
    s.display();
    
    // Remove particles that are "dead" (lifespan <= 0)
    if (s.isDead()) {
      stars.remove(i);
    }
  }
  
  // Display and update all waves
  for (int i = waves.size() - 1; i >= 0; i--) {
    Wave p = waves.get(i);
    p.applyRepelForce();  // Apply repel force before updating position
    p.update();
    p.display();
    
    // Remove waves that are "dead" (lifespan <= 0)
    if (p.isDead()) {
      waves.remove(i);
    }
  }
    
  // Check for beat
  if (millis() - lastBeatTime > beatInterval) {
    lastBeatTime = millis();
    size = lerp(size,100,0.1);
    onBeat();
  }
  
  fill(conducterColor);
  noStroke();
  ellipse(0, 0, size, size);
  
  // Debug information
  if (debugMode) {
    fill(0);
    textAlign(LEFT, TOP);
    textSize(14);
    text("Last OSC Message: " + lastOscMessage, 10, 10);
    text("FPS: " + nf(frameRate, 2, 1), 10, 30);
    text("Active Sections: " + getActiveSections(), 10, 50);
  }
}

// Function to create particles based on the sections and rows
void createSections() {
  float angleStep = (endAngle - startAngle) / mainSections;
  
  for (int i = 0; i < mainSections; i++) {
    float angle = startAngle + i * angleStep;  
    float nextAngle = angle + angleStep;  

    int rows = 2; // Default is 1 row if no subdivision happens
    if (i == 1 || i == 2) {
      rows = 4;  // Second and third columns have 4 rows
    }

    float rowStep = (outerRadius - innerRadius) / rows;

    for (int j = 0; j < rows; j++) {
      float innerRowRadius = innerRadius + j * rowStep;  
      float outerRowRadius = innerRadius + (j + 1) * rowStep; 
      if (i == 0 || i == 3){ 
        colSection = familyColors[0];
      } else{colSection = familyColors[j]; }
      // Check if it's the second or third column, and it's the second or third row
      if ((i == 1 || i == 2) && (j == 1 || j == 2)) {
        // Split the second and third rows into 2 sub-columns
        float columnStep = (nextAngle - angle) / 2;
        
        
        for (int k = 0; k < 2; k++) {
          float subAngle = angle + k * columnStep;  
          float nextSubAngle = subAngle + columnStep;  

          // Create a particle for each sub-column with a random color
          Section s = new Section(innerRowRadius, outerRowRadius, subAngle, nextSubAngle, colSection);
          sections.add(s);
        }
      } else {
        // Create a particle for each regular section 
        Section s = new Section(innerRowRadius, outerRowRadius, angle, nextAngle, colSection);
        sections.add(s);
      }
    }
  }
}


void oscEvent(OscMessage theOscMessage) {
  String addrPattern = theOscMessage.addrPattern();
  lastOscMessage = addrPattern; // Update for debug display
  
  if (addrPattern.startsWith("/midi/")) {
    try {
      int channel = Integer.parseInt(addrPattern.substring(6)) - 1; // MIDI channels are 1-indexed
      int status = theOscMessage.get(0).intValue();
      int note = theOscMessage.get(1).intValue();
      int velocity = theOscMessage.get(2).intValue();
      color pColor;
      
      if (status == 144 && velocity > 0 && channel < sections.size()) { // Note On
        xStar = random(-width/2,width/2);
        yStar = random(-height*0.9,-height/2);
        
        
        if (channel <= 2  || channel >= 14 || channel == 8 ){
          pColor = familyColors[0]; // String
          particles[note].activate(pColor, velocity,note);
        }else if ( channel == 7 || channel == 13){
          pColor = familyColors[3]; // Percussion
          // Add a new star every frame
          for (int i = 0; i < starsPerNote; i++) {
            stars.add(new Star(new PVector(xStar,yStar)));  // Spawn stars where clicked
          }
        }else if (channel == 3 || channel == 4 || channel == 9  || channel == 10){
          pColor = familyColors[1]; // Winds
          particles[note].activate(pColor, velocity,note);
        }else{
        pColor = familyColors[2]; // Brass
        // Spawn a set of waves at the mouse location
        for (int i = 0; i < wavesPerClick; i++) {
          waves.add(new Wave(new PVector(xStar, yStar), velocity, note));  // Spawn waves where clicked
        }
        //particles[note].activate(pColor,velocity,note);
      }
        
        sections.get(channel).playNote(note, velocity); // Play the note of the corresponding section
                
      } else if (status == 128 || (status == 144 && velocity == 0)) { // Note Off
        if (channel < sections.size()) sections.get(channel).noteOff();
      }
    } catch (Exception e) {
      println("Error parsing OSC message: " + addrPattern);
      e.printStackTrace();
    }
  } else if (addrPattern.equals("/tempo")) {
    try {
      bpm = theOscMessage.get(0).floatValue();
    } catch (Exception e) {
      println("Error parsing tempo message");
      e.printStackTrace();
    }
  }
}

// Debug toggle
void keyPressed() {
  if (key == 'd' || key == 'D') {
    debugMode = !debugMode;
    println("Debug mode: " + (debugMode ? "ON" : "OFF"));
  }
}

void onBeat() {
  if (conducterColor == 100){
    conducterColor = 180;
  }else{conducterColor = 100;}
  
}

String getActiveSections() {
  String active = "";
  for (Section section : sections) {
    if (section.isActive()) {
      active += section.name + ", ";
    }
  }
  return active.isEmpty() ? "None" : active.substring(0, active.length() - 2);
}

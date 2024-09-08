import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress myRemoteLocation;

float bpm = 100;
float lastBeatTime = 0;
float beatInterval;

// Orchestra sections
Section[] sections;

// Define sections based on the image, grouped by family
String[][] sectionFamilies = {
  {"VIOLIN", "SECOND VIOLIN", "VIOLA", "CELLO", "DOUBLE BASS"}, // Strings
  {"FLUTE", "OBOE", "CLARINET", "BASSOON"}, // Woodwinds
  {"FRENCH HORN", "TRUMPET", "TROMBONE", "TUBA"}, // Brass
  {"TIMPANI", "PERCUSSION", "HARP"} // Percussion and others (removed PICCOLO to match 16 channels)
};

color[] familyColors = {
  #4169E1, // Strings (Royal Blue)
  #228B22, // Woodwinds (Forest Green)
  #DAA520, // Brass (Goldenrod)
  #8B008B  // Percussion and others (Dark Magenta)
};

// Debug variables
boolean debugMode = false;
String lastOscMessage = "No message received yet";

// Background color
color backgroundColor;

void setup() {
  size(2000, 1000, P2D);
  frameRate(60);
  
  oscP5 = new OscP5(this, 57120);
  
  // Set static background color
  backgroundColor = color(51,51,51); // Light grayish-blue
  
  // Initialize orchestra sections
  sections = new Section[16]; // Explicitly set to 16 for MIDI channels
  
  int sectionIndex = 0;
  for (int f = 0; f < sectionFamilies.length; f++) {
    for (int i = 0; i < sectionFamilies[f].length; i++) {
      if (sectionIndex >= 16) break; // Ensure we don't exceed 16 sections
      float angle = map(sectionIndex, 0, 15, PI * 0.95, PI * 0.05);
      float radius = min(width, height) * 0.7;
      float x = width/2 + cos(angle) * radius;
      float y = height * 0.8 - sin(angle) * radius;
      sections[sectionIndex] = new Section(x, y, sectionFamilies[f][i], familyColors[f]);
      sectionIndex++;
    }
    if (sectionIndex >= 16) break; // Ensure we don't exceed 16 sections
  }
  
  println("Setup completed. Waiting for MIDI messages...");
}

void draw() {
  // Static background
  background(backgroundColor);
  
  beatInterval = 60000 / bpm;
  
  // Draw and update sections
  for (Section section : sections) {
    section.update();
    section.display();
  }
  
  // Draw conductor's position
  fill(100);
  ellipse(width/2, height * 0.7, 100, 100);
  
  // Check for beat
  if (millis() - lastBeatTime > beatInterval) {
    lastBeatTime = millis();
    onBeat();
  }
  
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

void oscEvent(OscMessage theOscMessage) {
  String addrPattern = theOscMessage.addrPattern();
  lastOscMessage = addrPattern; // Update for debug display
  
  if (addrPattern.startsWith("/midi/")) {
    try {
      int channel = Integer.parseInt(addrPattern.substring(6)) - 1; // MIDI channels are 1-indexed
      int status = theOscMessage.get(0).intValue();
      int note = theOscMessage.get(1).intValue();
      int velocity = theOscMessage.get(2).intValue();
      
      if (status == 144 && velocity > 0 && channel < sections.length) { // Note On
        sections[channel].playNote(note, velocity);
      } else if (status == 128 || (status == 144 && velocity == 0)) { // Note Off
        if (channel < sections.length) sections[channel].noteOff();
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

void onBeat() {
  for (Section section : sections) {
    section.onBeat();
  }
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

// Debug toggle
void keyPressed() {
  if (key == 'd' || key == 'D') {
    debugMode = !debugMode;
    println("Debug mode: " + (debugMode ? "ON" : "OFF"));
  }
}

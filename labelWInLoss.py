import pandas as pd
from fuzzywuzzy import fuzz

def classify_line(text, threshold=80):
    # Expanded phrases and keywords for winning and losing
    good_phrases = [
        "kill", "headshot", "frag", "eliminated", "multi-kill", "double kill", "triple kill", 
        "quad kill", "ace", "clutch", "secured kill", "dominant kill", "clean shot", "takedown", 
        "won the round", "victory", "secured the round", "flawless", "dominated the round", 
        "round win", "picked up the round", "secured match point", "clinched the round", 
        "defused", "detonated", "spike planted", "spike detonated", "bomb down","plant goes down", "spike down successfully",
        "advantage", "controlling the map", "strong hold", "perfect retake", "successful push", 
        "overwhelming", "executed perfectly", "perfect setup", "outplayed", "popped off", "on fire", 
        "unstoppable", "insane shot", "clutched up", "highlight play", "carried the team", 
        "ultimate usage perfect", "won the duel", "eco win", "thrifty win", "full buy", "buy round", 
        "force buy", "eco round success", "low buy success", "saved economy", "saved guns", 
        "strong economy", "economy control", "perfect flash", "well-placed smoke", "abilities forced them out",
        "hit with flash", "controlled site with utility", "great use of ult", "locked down the site", 
        "held strong crossfire", "team support", "good trades", "excellent coordination", "backed each other up", 
        "covered angles well", "strong map control", "secure flank", "held strong", "teamwork on point", "good", "great", "excellent", "strong", "effective", "impactful", "successful", "flawless", "dominant", 
    "solid", "secure", "strategic", "clean", "brilliant", "clutch", "controlled", "sharp", "on point", 
    "skilled", "victory", "win", "advantage", "gain", "lead", "synergy", "backup", "support", "teamwork", 
    "unstoppable", "overwhelming", "confident", "focused", "momentum", "ambitious", "resilient", "powerful"
    ]
    
    bad_phrases = [
         "eliminated", "killed", "fragged", "picked off", "taken out", "wiped out", "headshot against", 
        "caught off guard", "punished", "overpowered", "lost the round", "defeated", "round loss", 
        "couldn't hold", "failed to secure", "missed opportunity", "couldn’t close out", "couldn’t convert", 
        "struggled in round", "failed to execute", "failed to defuse", "spike defused by enemy", 
        "spike denied", "couldn't plant", "time expired", "bomb defused", "eco round failed", "poor buy", 
        "out of credits", "poor positioning", "outnumbered", "overwhelmed", "choked", "missed shots", 
        "failed clutch", "whiffed", "wasted ultimate", "bad timing", "lost eco round", "caught in smoke", 
        "blinded by flash", "hit by molly", "forced to reposition", "stuck in smoke", "utility missed", 
        "flash didn’t connect", "ultimate poorly timed", "missed flash", "abilities mistimed", 
        "smoke didn’t block vision", "caught in molly", "flashed and pushed", "cut off by utility", 
        "poor utility buy", "wasted credits on abilities", "no utility left for retake", "couldn’t afford abilities", 
        "bad timing on ability use", "knifed in the back","no dont do it too him", "no team support", "lost crossfire", 
        "poor cover", "failed trades", "disorganized", "caught without cover", "lost mid control", 
        "no map control", "split positioning", "poor map awareness", "caught without rotation", "bad", "poor", "weak", "ineffective", "unsuccessful", "sloppy", "messy", "exposed", "vulnerable", 
    "flawed", "disorganized", "struggle", "loss", "defeat", "setback", "mistake", "error", "gap", 
    "isolated", "unsupported", "uncoordinated", "miscommunication", "outmatched", "overwhelmed", 
    "pressured", "crushed", "dominated", "suffocated", "frustrated", "tired", "exhausted", 
    "low morale", "loss of momentum", "doubtful", "discouraged", "nervous", "tried"
    ]
    
    # Convert text to lowercase
    text = text.lower()
    
    # Check for good keywords using a combination of exact and fuzzy matching
    for phrase in good_phrases:
        if fuzz.partial_ratio(text, phrase.lower()) >= threshold or phrase in text:
            return 1  # Good play
    
    # Check for bad keywords
    for phrase in bad_phrases:
        if fuzz.partial_ratio(text, phrase.lower()) >= threshold or phrase in text:
            return 0  # Bad play
    
    # Default label if no match is found
    return ""

def label_transcript(transcript_df, threshold=80):
    # Apply the classification function to each line in the transcript
    transcript_df['Outcome'] = transcript_df['Text'].apply(lambda text: classify_line(text, threshold))
    return transcript_df

def main():
    transcript_file = "transcript.tsv"
    transcript_df = pd.read_csv(transcript_file, sep='\t')
    
    # Classify each line as Good (1) or Bad (0) with the updated matching criteria
    labeled_transcript = label_transcript(transcript_df, 80)
    
    # Save the labeled transcript to a new TSV file
    output_file = "labeled_transcript_with_outcomes.tsv"
    labeled_transcript.to_csv(output_file, sep='\t', index=False)
    print(f"Labeled transcript saved to {output_file}")

if __name__ == "__main__":
    main()
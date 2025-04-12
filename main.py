import gradio as gr
from transformers import pipeline
import os   
import shutil
import time
from moviepy import VideoFileClip
import subprocess

# Load the Hugging Face model pipeline
model = pipeline("automatic-speech-recognition", model=model1)

# Define paths for storing transcripts and audio files
transcript_file_path = "transcripts/consolidated_transcript.txt"
transcript_file_path_video = "transcripts/consolidated_transcript_video.txt"
audio_storage_path = "audio_files"
video_storage_path = "video_files"
os.makedirs("transcripts", exist_ok=True)
os.makedirs(audio_storage_path, exist_ok=True)
os.makedirs(video_storage_path, exist_ok=True)


# Ensure the consolidated transcript file exists
if not os.path.exists(transcript_file_path):
    with open(transcript_file_path, "w", encoding="utf-8") as f:
        f.write("")  # Create an empty file

if not os.path.exists(transcript_file_path_video):
    with open(transcript_file_path, "w", encoding="utf-8") as f:
        f.write("")  # Create an empty file

def get_unique_filename(folder, base_name, extension):
    """Generate a unique filename by appending a timestamp if necessary."""
    timestamp = int(time.time() * 1000)  # Milliseconds since epoch
    unique_name = f"{base_name}_{timestamp}{extension}"
    return os.path.join(folder, f"{base_name}_{timestamp}{extension}")

def process_audio(audio, name, gender, age, selected_languages, mother_tongue, region, spoken_terms, musical_experience, study_medium):
    if audio is None:
        return "No audio input provided."
    if not name or not gender or not age or not mother_tongue or not region or not spoken_terms or not study_medium:
        return "Please provide all required details before recording."
    
    try:
        base_name, extension = os.path.splitext(os.path.basename(audio))
        saved_audio_path = get_unique_filename(audio_storage_path, base_name, extension)
        shutil.copy(audio, saved_audio_path)


        transcription = model(saved_audio_path, return_timestamps=True)["text"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        line = (f"{os.path.basename(saved_audio_path)} | {timestamp} | {name} | Gender: {gender} | Age: {age} | Mother Tongue: {mother_tongue} | Region: {region} | "
                f"Spoken Terms: {spoken_terms} | Musical Exp: {musical_experience} | Medium of Study: {study_medium} | "
                f"Languages: {', '.join(selected_languages)} | Transcription: {transcription}\n")

        with open(transcript_file_path, "a", encoding="utf-8") as f:
            f.write(line)
        
        return f"Audio saved to: {saved_audio_path}\nTranscription added:\n{line.strip()}"
    except Exception as e:
        return f"Error processing audio: {str(e)}"

def process_video(video, name, gender, age, selected_languages, mother_tongue, region, spoken_terms, musical_experience, study_medium=None):
    if video is None:
        return "No video input provided."
    if not name or not gender or not age or not mother_tongue or not region or not spoken_terms or not study_medium:
        return "Please provide all required details before recording."
    try:
        # Generate a unique filename for the video file
        base_name, extension = os.path.splitext(os.path.basename(video))
        saved_video_path = get_unique_filename(video_storage_path, base_name, extension)

        # Save the uploaded video to the storage directory
        shutil.copy(video, saved_video_path)

        # Extract audio from the video using ffmpeg subprocess
        audio_path = get_unique_filename(audio_storage_path, base_name, ".wav")
        ffmpeg_command = [
            "ffmpeg", "-i", saved_video_path, "-vn", "-acodec", "pcm_s16le", audio_path
        ]
        subprocess.run(ffmpeg_command, check=True)

        # Process the extracted audio with the Hugging Face model
        transcription = model(audio_path, return_timestamps=True)["text"]

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Append the transcription to the consolidated file
        line_to_append = (f"{os.path.basename(audio_path)} | {timestamp} | {name} | Gender: {gender} | Age: {age} | Mother Tongue: {mother_tongue} | Region: {region} | "
                f"Spoken Terms: {spoken_terms} | Musical Exp: {musical_experience} | Medium of Study: {study_medium} | "
                f"Languages: {', '.join(selected_languages)} | Transcription: {transcription}\n")
        
        with open(transcript_file_path_video, "a", encoding="utf-8") as f:
            f.write(line_to_append)

        return f"Video saved to: {saved_video_path}\nAudio extracted and saved to: {audio_path}\nTranscription added to: {transcript_file_path_video}\n\n{line_to_append.strip()}"
    except subprocess.CalledProcessError as e:
        return f"Error processing video with ffmpeg: {e.output}"
    except Exception as e:
        return f"Error processing video: {str(e)}"


# Functions to control page visibility
def go_to_page2(name, gender, age, mother_tongue, region):
    if not all([name, gender, age, mother_tongue, region]):
        return gr.update(visible=True), gr.update(visible=False), "Please fill all required fields."
    return gr.update(visible=False), gr.update(visible=True), ""

def go_to_home():
    return gr.update(visible=True), gr.update(visible=False), ""

# Gradio Interface
with gr.Blocks() as app:
    # Page 1: Collect Gender, Age, and Proceed Button
    with gr.Column(visible=True) as page1:
        
        
        gr.Markdown(
            "<h2 style='text-align: center; margin: 0;'> Welcome to the Application</h2>"
            
            )
        gr.Markdown(
            "<p style='text-align: center; margin: 0;'>Provide your details below and proceed to record your voice.</p>"
            
            )
        
        #inputs
        name_input = gr.Textbox(label="Name")
        gender_input = gr.Dropdown(choices=["Male", "Female", "Other"], label="Gender")
        age_input = gr.Number(label="Age")
        mother_tongue_input = gr.Textbox(label="Mother Tongue")
        region_input = gr.Textbox(label="Region/Place of Living")
        spoken_terms_input = gr.Textbox(label="Spoken Terms")
        musical_exp_input = gr.Checkbox(label="Any experience in musical study?")
        medium_study_input = gr.Textbox(label="Medium of Study (School, High School, UG, PG)")
        
        language_options = ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "Marathi", "Bengali", "Gujarati"]
        selected_languages = gr.Dropdown(choices=language_options, label="Select Languages You Know", multiselect=True)
        
        error_msg = gr.Textbox(visible=False)
        next_btn = gr.Button("Proceed to record")
        

    # Page 2: Recording Button, Audio Upload, and Home Button
    with gr.Column(visible=False) as page2:
        # with gr.Row():  # Row layout for side-by-side images
        #     gr.Image("logo1.png", label=None, width=100, height=100, elem_id="logo1")
        #     gr.Image("logo2.png", label=None, width=100, height=100, elem_id="logo2")
        gr.Markdown("# Record Your Voice")
        gr.Markdown("Press the button below to start recording your voice or upload an audio file.")
        
        with gr.Tab("Audio Upload"):
            audio_input = gr.Audio(type="filepath", label="Upload Audio")
            audio_output = gr.Textbox(label="Transcription Result")
            audio_button = gr.Button("Transcribe Audio")
            audio_button.click(process_audio, 
                           inputs=[audio_input, name_input, gender_input, age_input, selected_languages, 
                                   mother_tongue_input, region_input, spoken_terms_input, 
                                   musical_exp_input, medium_study_input], 
                           outputs=audio_output) 
        with gr.Tab("Video Upload"):
            video_input = gr.Video(label="Upload Video")
            video_output = gr.Textbox(label="Transcription Result")
            video_button = gr.Button("Transcribe Video")
            video_button.click(process_video, 
                           inputs=[video_input, name_input, gender_input, age_input, selected_languages, 
                                   mother_tongue_input, region_input, spoken_terms_input, 
                                   musical_exp_input, medium_study_input], 
                           outputs=video_output)  
        home_btn = gr.Button("Home")

    # Button actions for navigation
    next_btn.click(go_to_page2, inputs=[name_input, gender_input, age_input, mother_tongue_input, region_input], outputs=[page1, page2, error_msg])
    home_btn.click(go_to_home, outputs=[page1, page2, error_msg])

# Launch the app
app.launch(share=True)

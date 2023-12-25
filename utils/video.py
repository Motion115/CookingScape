import os
import scenedetect
import json
'''
Prequsite:
- Ensure that ffmpeg is installed and add to system path
- Ensure that you installed OpenAI Whisper model
'''

class Video:
    def __init__(self, file_path, file_name, encoding, ASR_model_path):
        self.file_path = file_path
        self.file_name = file_name
        self.encoding = encoding
        self.ASR_model_path = ASR_model_path
        self.open_file()
        self.transcribe()
        # self.extract_key_frames()
        self.detect_scenes()
    
    def open_file(self):
        # assemble the file_path and check if exist
        file_path = os.path.join(self.file_path, self.file_name + self.encoding)
        if os.path.exists(file_path):
            print(f"- Processing {file_path}")
        else:
            print(f"- File {file_path} does not exist.")
            return

        # make a .cache folder if there is not one
        if not os.path.exists('.cache'):
            os.makedirs('.cache')

        if not os.path.exists('.cache/' + self.file_name):
            os.makedirs('.cache/' + self.file_name)
            # use ffmpeg to split the audio from the original video
            target_audio_path = os.path.join('.cache/' + self.file_name, self.file_name + '.mp3')
            target_video_path = os.path.join('.cache/' + self.file_name, self.file_name + '.mp4')
            os.system(f"ffmpeg -i {file_path} -c:v copy -an {target_video_path} -vn -acodec libmp3lame -q:a 2 {target_audio_path}")
        else:
            print(f"- Folder .cache/{self.file_name} already exists.")
            return
        
    def transcribe(self):
        if not os.path.exists('.cache/' + self.file_name + "/" + self.file_name + ".json"):
            print(f"- Generating transcription w/ OpenAI Whisper")
            audio_path = os.path.join('.cache/' + self.file_name, self.file_name + '.mp3')
            output_path = os.path.join('.cache/' + self.file_name)
            os.system(f'whisper --model_dir={self.ASR_model_path} --output_dir={output_path} {audio_path} --verbose=False')
        else:
            print(f"- Transcription already exists for {self.file_name}.mp4")
    
    def extract_key_frames(self):
        if not os.path.exists('.cache/' + self.file_name + "/iFrame"):
            print(f"- Extracting key frames")
            key_frames_path = os.path.join('.cache/' + self.file_name, "iFrame/")
            # create this folder
            if not os.path.exists(key_frames_path):
                os.makedirs(key_frames_path)
            video_path = os.path.join('.cache/' + self.file_name, self.file_name + '.mp4')
            os.system(f'''ffmpeg -i {video_path} -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr {key_frames_path}%03d.jpg''')
        else:
            print(f"- Key frames already exist for {self.file_name}.mp4")
    
    def detect_scenes(self):
        if not os.path.exists('.cache/' + self.file_name + "/scene"):
            print(f"- Detecting scene")
            storage_path = os.path.join('.cache/' + self.file_name, "scene/")
            # create this folder
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)
            video_path = os.path.join('.cache/' + self.file_name, self.file_name + '.mp4')
            scene_list, video_stream = self._find_scenes(video_path, storage_path)
            scenedetect.scene_manager.save_images(
                scene_list = scene_list,
                video = video_stream,
                num_images = 1,
                output_dir = storage_path,
            )
            # create an empty file called scene_list.csv
            with open('.cache/' + self.file_name + '/scene_list.csv', 'w') as f:
                scenedetect.scene_manager.write_scene_list(f, scene_list, include_cut_list=False)
                f.close()
        else:
            print(f"- Scene already exists for {self.file_name}.mp4")

    def _find_scenes(self, video_path, storage_path, threshold=27.0):
        video = scenedetect.open_video(video_path)
        scene_manager = scenedetect.SceneManager()
        scene_manager.add_detector(
            scenedetect.ContentDetector(threshold=threshold))
        # Detect all scenes in video from current position to end.
        scene_manager.detect_scenes(video, show_progress=True)
        # `get_scene_list` returns a list of start/end timecode pairs
        # for each scene that was found.
        return scene_manager.get_scene_list(), video
    
    def get_transcript(self, separator=None) -> list:
        # read './cache' + file_name + file_name.json
        json_transcript_path = '.cache/' + self.file_name + '/' + self.file_name + '.json'
        with open(json_transcript_path, 'r') as f:
            data = json.load(f)
            f.close()
        full_transcript = data["text"]
        if separator is not None:
            # split the full_transcript into a list by separator
            sentence_list = full_transcript.split(separator)
            # strip extra spaces
            sentence_list = [sentence.strip() for sentence in sentence_list]
            return [sentence + separator for sentence in sentence_list]
        else:
            return [full_transcript]


            
            
            

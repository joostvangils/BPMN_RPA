import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
import time

# The BPMN-RPA Azure module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Azure module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Azure_Speech:

    def __init__(self, subscription_id, region="westeurope", language="nl-NL"):
        """
        Initialize the Azure Speech class.
        :param subscription_id: The Azure subscription ID.
        :param region: Optional. The Azure region. Default is westeurope.
        :param language: Optional. The language. Default is nl-NL.
        """
        self.language = language
        self.region = region
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription_id, region=region, speech_recognition_language=language)
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    def speak_text_to_file(self, text, filename, voice_name="nl-NL-ColetteNeural"):
        """
        Speak text to a file.
        :param text: The text to speak.
        :param filename: The filename to save the audio to.
        :param voice_name: Optional. The voice to use. Default is nl-NL-ColetteNeural.
        """
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        ssml = f'''
        <speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{self.language}">
          <voice name="{voice_name}">
                {text}
          </voice>
        </speak>
        '''
        ssml_string = ssml
        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)
        if not filename.lower().endswith(".wav"):
            filename = filename + ".wav"
        stream.save_to_wav_file(f"{filename}")

    def speak_text(self, text, voice_name="nl-NL-ColetteNeural"):
        """
        Speak text.
        :param text: The text to speak.
        :param voice_name: Optional. The voice to use. Default is nl-NL-ColetteNeural.
        """
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        ssml = f'''
        <speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{self.language}">
          <voice name="{voice_name}">
                {text}
          </voice>
        </speak>
        '''
        ssml_string = ssml
        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)

    def speak_file(self, filename, voice_name="nl-NL-ColetteNeural"):
        """
        Speak a file.
        :param filename: The filename that holds the text to speak.
        :param voice_name: Optional. The voice to use. Default is nl-NL-ColetteNeural.
        """
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        text = open(filename, "r").read()
        ssml = f'''
        <speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="{self.language}">
          <voice name="{voice_name}">
                {text}
          </voice>
        </speak>
        '''
        ssml_string = ssml
        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)

    def speak_ssml(self, ssml, voice_name="nl-NL-ColetteNeural"):
        """
        Speak Speech Synthesis Markup Language (SSML)
        :param ssml: The SSML to speak.
        :param voice_name: Optional. The voice to use. Default is nl-NL-ColetteNeural.
        """
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        ssml_string = ssml
        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)

    def speak_ssml_file(self, filename, voice_name="nl-NL-ColetteNeural"):
        """
        Speak a file that contains Speech Synthesis Markup Language (SSML).
        :param filename: The filename that holds the SSML to speak.
        :param voice_name: Optional. The voice to use. Default is nl-NL-ColetteNeural.
        """
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        ssml = open(filename, "r").read()
        ssml_string = ssml
        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)

class Azure_Vision:

    def __init__(self, subscription_id, end_point, region="westeurope"):
        """
        Initialize the Azure Vision class.
        :param subscription_id: Azure subscription id
        :param end_point: Azure end point of your Computer Vision resource.
        :param region: Optional. Azure region. Default is westeurope.
        """
        self.end_point = end_point
        self.subscription_id = subscription_id
        self.region = region

    def get_text_from_image(self, image_path):
        """
        Get text from image.
        :param image_path: Path to image.
        :return: Text from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        read_response = computervision_client.read_in_stream(local_image, raw=True)
        operation_location_remote = read_response.headers["Operation-Location"]
        operation_id = operation_location_remote.split("/")[-1]
        while True:
            get_handw_text_results = computervision_client.get_read_result(operation_id)
            if get_handw_text_results.status not in ['notStarted', 'running']:
                break
            time.sleep(1)
        text = ""
        for line in get_handw_text_results.analyze_result.read_results[0].lines:
            text = text + line.text + "\n"
        return text

    def get_objects_from_image(self, image_path):
        """
        Get objects from image.
        :param image_path: Path to image.
        :return: Objects from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        objects = computervision_client.detect_objects_in_stream(local_image)
        return objects

    def get_tags_from_image(self, image_path):
        """
        Get tags from image.
        :param image_path: Path to image.
        :return: Tags from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        tags_result_remote = computervision_client.tag_image_in_stream(local_image)
        return tags_result_remote

    def get_description_from_image(self, image_path):
        """
        Get description from image.
        :param image_path: Path to image.
        :return: Description from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        description_results = computervision_client.describe_image_in_stream(local_image)
        return description_results

    def get_faces_from_image(self, image_path):
        """
        Get faces from image.
        :param image_path: Path to image.
        :return: Faces from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        detect_faces_results_remote = computervision_client.detect_faces_in_stream(local_image)
        return detect_faces_results_remote

    def get_brands_from_image(self, image_path):
        """
        Get brands from image.
        :param image_path: Path to image.
        :return: Brands from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        brands_results_remote = computervision_client.analyze_image_by_domain_in_stream("landmarks", local_image)
        return brands_results_remote

    def get_landmarks_from_image(self, image_path):
        """
        Get landmarks from image.
        :param image_path: Path to image.
        :return: Landmarks from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        landmarks_results_remote = computervision_client.analyze_image_by_domain_in_stream("landmarks", local_image)
        return landmarks_results_remote

    def get_adult_content_from_image(self, image_path):
        """
        Get adult content from image.
        :param image_path: Path to image.
        :return: Adult content from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        adult_results_remote = computervision_client.analyze_image_by_domain_in_stream("adult", local_image)
        return adult_results_remote

    def get_celebrities_from_image(self, image_path):
        """
        Get celebrities from image.
        :param image_path: Path to image.
        :return: Celebrities from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        celebrities_results_remote = computervision_client.analyze_image_by_domain_in_stream("celebrities", local_image)
        return celebrities_results_remote

    def get_color_from_image(self, image_path):
        """
        Get color from image.
        :param image_path: Path to image.
        :return: Color from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        color_results_remote = computervision_client.analyze_image_by_domain_in_stream("color", local_image)
        return color_results_remote

    def get_image_type_from_image(self, image_path):
        """
        Get image type from image.
        :param image_path: Path to image.
        :return: Image type from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        image_type_results_remote = computervision_client.analyze_image_by_domain_in_stream("imageType", local_image)
        return image_type_results_remote

    def get_image_details_from_image(self, image_path):
        """
        Get image details from image.
        :param image_path: Path to image.
        :return: Image details from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        details_results_remote = computervision_client.analyze_image_by_domain_in_stream("details", local_image)
        return details_results_remote

    def get_image_captions_from_image(self, image_path):
        """
        Get image captions from image.
        :param image_path: Path to image.
        :return: Image captions from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        captions_results_remote = computervision_client.analyze_image_by_domain_in_stream("captions", local_image)
        return captions_results_remote

    def get_image_categories_from_image(self, image_path):
        """
        Get image categories from image.
        :param image_path: Path to image.
        :return: Image categories from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        categories_results_remote = computervision_client.analyze_image_by_domain_in_stream("categories", local_image)
        return categories_results_remote

    def get_people_in_image(self, image_path):
        """
        Get people in image.
        :param image_path: Path to image.
        :return: People in image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        person_results_remote = computervision_client.analyze_image_by_domain_in_stream("people", local_image)
        return person_results_remote

    def get_area_of_interest_in_image(self, image_path):
        """
        Get area of interest in image.
        :param image_path: Path to image.
        :return: Area of interest in image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        area_of_interest_results_remote = computervision_client.analyze_image_by_domain_in_stream("areaOfInterest", local_image)
        return area_of_interest_results_remote

    def get_available_domains(self):
        """
        Get available domains.
        :return: Available domains.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        available_domains = computervision_client.list_domain_specific_models()
        return available_domains

    def get_domain_in_image(self, image_path, domain):
        """
        Get domain in image.
        :param image_path: Path to image.
        :param domain: Domain to get.
        :return: Domain in image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        domain_results_remote = computervision_client.analyze_image_by_domain_in_stream(domain, local_image)
        return domain_results_remote

    def get_image_description_from_image(self, image_path):
        """
        Get image description from image.
        :param image_path: Path to image.
        :return: Image description from image.
        """
        computervision_client = ComputerVisionClient(endpoint=self.end_point, credentials=CognitiveServicesCredentials(self.subscription_id))
        local_image = open(image_path, "rb")
        description_results_remote = computervision_client.describe_image_in_stream(local_image)
        return description_results_remote


from googletrans import Translator

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'ar': 'Arabic',
            'ur': 'Urdu'
        }
    
    def translate_text(self, text, target_language='ar'):
        try:
            if target_language == 'en':
                return text
            
            result = self.translator.translate(text, dest=target_language)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def get_translations(self, texts, target_language='ar'):
        translations = {}
        for key, text in texts.items():
            translations[key] = self.translate_text(text, target_language)
        return translations

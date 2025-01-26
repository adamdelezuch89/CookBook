from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import pytesseract
from PIL import Image, ImageEnhance
import re
import openai
import os
from dotenv import load_dotenv

load_dotenv()


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa etykiety")

    class Meta:
        verbose_name = "Etykieta"
        verbose_name_plural = "Etykiety"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nazwa Przepisu")
    description = models.TextField(blank=True, null=True, verbose_name="Opis")
    image = models.ImageField(
        upload_to="recipes/", blank=True, null=True, verbose_name="Zdjęcie"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        verbose_name="Ocena",
    )
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Kategorie")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Etykiety")

    prep_time = models.IntegerField(
        blank=True, null=True, verbose_name="Czas przygotowania (min)"
    )
    cook_time = models.IntegerField(
        blank=True, null=True, verbose_name="Czas gotowania (min)"
    )
    idle_time = models.IntegerField(
        blank=True, null=True, verbose_name="Czas bezczynności (min)"
    )
    total_time = models.IntegerField(
        blank=True, null=True, verbose_name="Czas całkowity (min)"
    )

    servings = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Liczba porcji"
    )
    ingredients = models.TextField(blank=True, null=True, verbose_name="Składniki")
    instructions = models.TextField(
        blank=True, null=True, verbose_name="Sposób przygotowania"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Uwagi")
    nutrition = models.TextField(
        blank=True, null=True, verbose_name="Wartości odżywcze"
    )
    equipment = models.TextField(blank=True, null=True, verbose_name="Naczynia")
    video = models.URLField(blank=True, null=True, verbose_name="Link do filmu")
    source = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Źródło"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data modyfikacji")

    class Meta:
        verbose_name = "Przepis"
        verbose_name_plural = "Przepisy"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ScannedRecipe(models.Model):
    image = models.ImageField(
        upload_to="scanned_recipes/", verbose_name="Zeskanowany obraz"
    )
    scanned_text = models.TextField(
        blank=True, null=True, verbose_name="Rozpoznany tekst"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def extract_text(self):
        """Extract recipe from image using OpenAI Vision."""
        if not self.image:
            return

        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompt = """
            Przeanalizuj zdjęcie przepisu kulinarnego i zwróć informacje w formacie JSON. Odpowiedz dokładnie w tym formacie, bez żadnego dodatkowego tekstu:
            {
                "name": "Nazwa przepisu",
                "description": "Krótki opis przepisu",
                "prep_time": liczba (w minutach),
                "cook_time": liczba (w minutach),
                "idle_time": liczba (w minutach),
                "total_time": liczba (w minutach),
                "servings": liczba porcji,
                "ingredients": "Lista składników - każdy punkt niech będzie oddzielony enterem, a zaczyna się cyfrą (int), np:
                     1 szczypta soli, 
                     2 ząbki czosnku, 
                     3 łyżki oleju,
                     1/2 łyżeczki sody
                     Pamiętaj żeby dodać ilość/miarę int przy każdym składniku!",
                "instructions": "Instrukcje przygotowania krok po kroku. Oddziel kroki enterami, ale nie numeruj ich!",
                "notes": "Dodatkowe uwagi",
                "nutrition": "Informacje o wartościach odżywczych",
                "equipment": "Potrzebne naczynia i sprzęt",
                "source": "Źródło przepisu (jeśli podane)"
            }

            Jeśli jakieś pole nie jest dostępne w przepisie, zostaw null. Dla pól czasowych użyj liczb całkowitych (w minutach).
            Nie dodawaj żadnych komentarzy ani dodatkowego tekstu przed lub po JSONie.
            Nie numeruj składników ani instrukcji, ale pamiętaj o oddzielaniu punktów enterami
            """

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{self._get_image_base64()}"
                                },
                            },
                        ],
                    }
                ],
            )

            # Get the response and clean it up
            raw_response = response.choices[0].message.content
            print("Raw response:", raw_response)  # Debug print
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                self.scanned_text = json_match.group()
            else:
                self.scanned_text = raw_response
            
            print("Cleaned response:", self.scanned_text)  # Debug print
            self.save()

        except Exception as e:
            print(f"Error during OpenAI analysis: {str(e)}")
            raise

    def _get_image_base64(self):
        """Convert image to base64 string."""
        import base64

        with open(self.image.path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def create_recipe(self):
        """Create Recipe object from scanned text."""
        if not self.scanned_text:
            return None

        try:
            import json
            # Try to clean up the text before parsing
            text_to_parse = self.scanned_text.strip()
            print("Attempting to parse:", text_to_parse)  # Debug print
            
            try:
                recipe_data = json.loads(text_to_parse)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                # Try to fix common JSON issues
                text_to_parse = text_to_parse.replace("'", '"')  # Replace single quotes with double quotes
                text_to_parse = re.sub(r'(\w+):', r'"\1":', text_to_parse)  # Add quotes to keys
                recipe_data = json.loads(text_to_parse)

            # Utwórz przepis ze wszystkimi dostępnymi polami
            return Recipe.objects.create(
                name=recipe_data.get("name", "Nowy przepis"),
                description=recipe_data.get("description"),
                prep_time=recipe_data.get("prep_time"),
                cook_time=recipe_data.get("cook_time"),
                idle_time=recipe_data.get("idle_time"),
                total_time=recipe_data.get("total_time"),
                servings=recipe_data.get("servings"),
                ingredients=recipe_data.get("ingredients"),
                instructions=recipe_data.get("instructions"),
                notes=recipe_data.get("notes"),
                nutrition=recipe_data.get("nutrition"),
                equipment=recipe_data.get("equipment"),
                source=recipe_data.get("source"),
            )

        except Exception as e:
            print(f"Error creating recipe: {str(e)}")
            return None

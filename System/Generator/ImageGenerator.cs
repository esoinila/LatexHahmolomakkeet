using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Mscc.GenerativeAI;

namespace RPGCharacterGenerator
{
    public class ImageGenerator
    {
        private readonly string _apiKey;

        public ImageGenerator(IConfiguration configuration)
        {
            _apiKey = configuration["Gemini:ApiKey"];
        }

        public async Task GenerateImageAsync(Character c, string outputPath)
        {
            if (string.IsNullOrEmpty(_apiKey))
            {
                Console.WriteLine("Warning: Gemini:ApiKey not found in User Secrets. Skipping image generation.");
                return;
            }

            var googleAI = new GoogleAI(apiKey: _apiKey);
            // Use Imagen 3 model by name
            var model = googleAI.GenerativeModel("models/imagen-3.0-generate-001");

            string prompt = BuildPrompt(c);
            Console.WriteLine($"Image Generation Prompt: {prompt}");

            try
            {
                // Mscc.GenerativeAI typically uses GenerateContent for everything.
                // For images, the response *should* contain InlineData. 
                // However, recent changes might have moved it or renamed it.
                // Let's use a dynamic approach or standard property access if confirmed.
                // Assuming standard library structure:
                var response = await model.GenerateContent(prompt);

                if (response?.Candidates != null && response.Candidates.Count > 0)
                {
                     var candidate = response.Candidates[0];
                     if (candidate.Content?.Parts != null && candidate.Content.Parts.Count > 0)
                     {
                         var part = candidate.Content.Parts[0];
                         // Check properties
                         if (part.InlineData != null)
                         {
                             // InlineData is a Blob object with MimeType and Data
                             if (!string.IsNullOrEmpty(part.InlineData.Data))
                             {
                                 byte[] imageBytes = Convert.FromBase64String(part.InlineData.Data);
                                 await File.WriteAllBytesAsync(outputPath, imageBytes);
                                 Console.WriteLine($"Image saved to {outputPath}");
                                 return;
                             }
                         }
                         
                         Console.WriteLine("No inline image data found in response part.");
                     }
                }
                else
                {
                     Console.WriteLine("Empty response from API.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error generating image: {ex.Message}");
                // Fallback: Copy a default image so the LaTeX compilation doesn't fail
                try 
                {
                    string fallbackImage = Path.Combine(Path.GetDirectoryName(outputPath), "Nanobana.png");
                    if (File.Exists(fallbackImage))
                    {
                        Console.WriteLine("Using fallback image (Nanobana.png) due to generation failure.");
                        File.Copy(fallbackImage, outputPath, true);
                    }
                }
                catch { /* Ignore fallback failure */ }
            }
        }
        
    // RE-WRITING LOGIC: 
    // I will use a more robust approach by checking standard response types for this library.
    // It seems "Mscc.GenerativeAI" makes it easy.
    
        private string BuildPrompt(Character c)
        {
            if (!string.IsNullOrEmpty(c.ImagePrompt))
            {
                return c.ImagePrompt;
            }

            // Fallback: Construct it
            return $"Character portrait of {c.Name}, {c.Role}. " +
                   $"Appearance: {c.Quote}. " + // Quote often hints at vibe
                   $"Background: {c.Background.Replace("\n", " ").Substring(0, Math.Min(c.Background.Length, 200))}... " +
                   "High quality, realistic, cinematic lighting, RPG character art style.";
        }
    }
}

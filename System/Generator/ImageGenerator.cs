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
            // Use Imagen 3 model
            var model = googleAI.GenerativeModel(Model.Imagen3);

            string prompt = BuildPrompt(c);
            Console.WriteLine($"Image Generation Prompt: {prompt}");

            try
            {
                // Correct usage for Mscc.GenerativeAI assuming standard response pattern
                var response = await model.GenerateContent(prompt);

                if (response != null && response.Candidates != null && response.Candidates.Count > 0)
                {
                     var candidate = response.Candidates[0];
                     if (candidate.Content != null && candidate.Content.Parts != null && candidate.Content.Parts.Count > 0)
                     {
                         var part = candidate.Content.Parts[0];
                         if (part.InlineData != null && !string.IsNullOrEmpty(part.InlineData.Data))
                         {
                             // It's base64 encoded
                             byte[] imageBytes = Convert.FromBase64String(part.InlineData.Data);
                             await File.WriteAllBytesAsync(outputPath, imageBytes);
                             Console.WriteLine($"Image saved to {outputPath}");
                         }
                         else
                         {
                             Console.WriteLine("No inline data found in response.");
                         }
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

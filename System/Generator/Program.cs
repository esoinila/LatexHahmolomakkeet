
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;

namespace RPGCharacterGenerator
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("RPG Character Generator");

            // Setup Configuration for User Secrets
            var builder = new ConfigurationBuilder()
                .AddUserSecrets<Program>();
            var configuration = builder.Build();

            string currentDir = Directory.GetCurrentDirectory();
            // Assuming running from System/Generator or pointing to it. 
            // If running "dotnet run" inside System/Generator, root is two levels up.
            string rootDir = Path.GetFullPath(Path.Combine(currentDir, "..", ".."));
            string inputDir = Path.Combine(rootDir, "Characters");
            string templatesDir = Path.Combine(currentDir, "Templates");
            string outputDir = Path.Combine(rootDir, "System", "Temp");
            string imagesDir = Path.Combine(rootDir, "images");

            if (!Directory.Exists(inputDir))
            {
                Console.WriteLine($"Input directory not found: {inputDir}");
                return;
            }
            if (!Directory.Exists(imagesDir))
            {
                Directory.CreateDirectory(imagesDir);
            }

            var parser = new MarkdownParser();
            var generator = new TexGenerator();
            var imageGen = new ImageGenerator(configuration);

            string charTemplatePath = Path.Combine(templatesDir, "template_character.tex");
            string signTemplatePath = Path.Combine(templatesDir, "template_namesign.tex");

            if (!File.Exists(charTemplatePath) || !File.Exists(signTemplatePath))
            {
                Console.WriteLine("Templates not found in " + templatesDir);
                return;
            }

            var mdFiles = Directory.GetFiles(inputDir, "*.md");
            if (mdFiles.Length == 0)
            {
                Console.WriteLine("No markdown files found in " + inputDir);
            }

            foreach (var file in mdFiles)
            {
                try
                {
                    Console.WriteLine($"Processing {Path.GetFileName(file)}...");
                    Character c = parser.Parse(file);

                    // Check for image
                    string imagePath = Path.Combine(imagesDir, c.Image);
                    if (!File.Exists(imagePath))
                    {
                        Console.WriteLine($"  Image not found: {c.Image}. Attempting to generate...");
                        await imageGen.GenerateImageAsync(c, imagePath);
                    }
                    
                    // Specific naming convention: character_Firstname.tex
                    string firstName = c.Name.Split(' ')[0];
                    string charOutputPath = Path.Combine(outputDir, $"character_{firstName}.tex");
                    string signOutputPath = Path.Combine(outputDir, $"namesign_{firstName}.tex");

                    Console.WriteLine($"  Generating {Path.GetFileName(charOutputPath)}");
                    generator.GenerateCharacterSheet(c, charTemplatePath, charOutputPath);

                    Console.WriteLine($"  Generating {Path.GetFileName(signOutputPath)}");
                    generator.GenerateNameSign(c, signTemplatePath, signOutputPath);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error processing {file}: {ex.Message}");
                }
            }

            Console.WriteLine("Done!");
        }
    }
}

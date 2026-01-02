
using System;
using System.IO;

namespace RPGCharacterGenerator
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("RPG Character Generator");

            string currentDir = Directory.GetCurrentDirectory();
            string rootDir = Path.GetFullPath(Path.Combine(currentDir, ".."));
            string inputDir = Path.Combine(rootDir, "Characters");
            string templatesDir = Path.Combine(currentDir, "Templates");
            string outputDir = rootDir;

            if (!Directory.Exists(inputDir))
            {
                Console.WriteLine($"Input directory not found: {inputDir}");
                return;
            }

            var parser = new MarkdownParser();
            var generator = new TexGenerator();

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

                    // Filename sanitization
                    string safeName = c.Name.Replace(" ", "").Replace("@", "");
                    
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

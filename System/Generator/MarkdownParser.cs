
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RPGCharacterGenerator
{
    public class MarkdownParser
    {
        public Character Parse(string filePath)
        {
            var lines = File.ReadAllLines(filePath);
            var character = new Character();
            string currentSection = "";
            
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (string.IsNullOrWhiteSpace(trimmed)) continue;

                if (trimmed.StartsWith("# "))
                {
                    currentSection = trimmed.TrimStart('#', ' ');
                }
                else if (trimmed.StartsWith("## "))
                {
                    currentSection = trimmed.Substring(3).Trim();
                }
                else
                {
                    ProcessLine(character, currentSection, trimmed);
                }
            }

            return character;
        }

        private void ProcessLine(Character c, string section, string line)
        {
            switch (section.ToLower())
            {
                case "name":
                    var match = Regex.Match(line, @"^(.*?)\s+(@\S+)$");
                    if (match.Success)
                    {
                        c.Name = match.Groups[1].Value;
                        c.Handle = match.Groups[2].Value;
                    }
                    else
                    {
                        c.Name = line;
                        c.Handle = "";
                    }
                    break;
                case "image":
                    c.Image = line;
                    break;
                case "image prompt":
                    c.ImagePrompt = AppendText(c.ImagePrompt, line);
                    break;
                case "quote":
                    c.Quote = AppendText(c.Quote, line);
                    break;
                case "role":
                case "summary":
                    c.Role = AppendText(c.Role, line);
                    break;
                case "personal quest":
                    c.PersonalQuest = AppendText(c.PersonalQuest, line);
                    break;
                case "key entity":
                case "key contact":
                case "key rival":
                    c.KeyEntity = AppendText(c.KeyEntity, line);
                    break;
                case "abilities":
                    if (line.StartsWith("- ")) c.Abilities.Add(line.Substring(2));
                    else c.Abilities.Add(line);
                    break;
                case "core personality":
                case "personality":
                    if (line.StartsWith("- ")) c.Personality.Add(line.Substring(2));
                    else c.Personality.Add(line);
                    break;
                case "stress response":
                case "handicaps":
                    if (line.StartsWith("- ")) c.StressResponse.Add(line.Substring(2));
                    else c.StressResponse.Add(line);
                    break;
                case "equipment":
                    if (line.StartsWith("- ")) c.Equipment.Add(line.Substring(2));
                    else c.Equipment.Add(line);
                    break;
                case "background":
                    c.Background = AppendText(c.Background, line);
                    break;
            }
        }

        private string AppendText(string current, string next)
        {
            if (string.IsNullOrEmpty(current)) return next;
            return current + " " + next;
        }
    }
}

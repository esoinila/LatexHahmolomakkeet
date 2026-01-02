
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace RPGCharacterGenerator
{
    public class TexGenerator
    {
        public void GenerateCharacterSheet(Character c, string templatePath, string outputPath)
        {
            var content = File.ReadAllText(templatePath);

            content = ReplaceTag(content, "IMAGE", c.Image);
            content = ReplaceTag(content, "NAME_AND_HANDLE", Escape(c.FullName));
            
            // Construct Background
            var bgBuilder = new StringBuilder();
            bgBuilder.Append(FormatMarkdown(c.Background));
            
            if (!string.IsNullOrEmpty(c.PersonalQuest))
            {
                bgBuilder.Append(@" \newline \newline \textbf{Personal Quest:} ");
                bgBuilder.Append(FormatMarkdown(c.PersonalQuest));
            }

            if (!string.IsNullOrEmpty(c.KeyEntity))
            {
                bgBuilder.Append(@" \newline \newline ");
                bgBuilder.Append(FormatMarkdown(c.KeyEntity));
            }

            content = ReplaceTag(content, "BACKGROUND", bgBuilder.ToString());

            // Lists
            content = ReplaceTag(content, "ABILITIES", FormatListGrid(c.Abilities));
            content = ReplaceTag(content, "PERSONALITY", FormatListGrid(c.Personality)); // 2 chosen
            content = ReplaceTag(content, "STRESS_RESPONSE", FormatListGrid(c.StressResponse)); // 2 chosen
            content = ReplaceTag(content, "EQUIPMENT", FormatListGrid(c.Equipment, columns: 2));

            File.WriteAllText(outputPath, content);
        }

        public void GenerateNameSign(Character c, string templatePath, string outputPath)
        {
            var content = File.ReadAllText(templatePath);

            content = ReplaceTag(content, "IMAGE", c.Image);
            content = ReplaceTag(content, "NAME", Escape(c.Name));
            content = ReplaceTag(content, "QUOTE", Escape(c.Quote));

            File.WriteAllText(outputPath, content);
        }

        private string ReplaceTag(string content, string tag, string value)
        {
            return content.Replace($"[[{tag}]]", value);
        }

        private string FormatListGrid(List<string> items, int columns = 2)
        {
            var sb = new StringBuilder();
            for (int i = 0; i < items.Count; i++)
            {
                sb.Append(Escape(items[i]));
                if ((i + 1) % columns == 0 && i != items.Count - 1)
                {
                    sb.Append(@" \newline \newline ");
                }
                else if (i != items.Count - 1)
                {
                    sb.Append(@" \qquad \hspace{5mm} ");
                }
            }
            return sb.ToString();
        }

        private string Escape(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            // Characters to escape: # $ % & ~ _ ^ \ { }
            // Note: We need to avoid double escaping if we run this multiple times.
            // But strict escaping is safer.
            return text
                .Replace("\\", "\\textbackslash{}")
                .Replace("{", "\\{")
                .Replace("}", "\\}")
                .Replace("$", "\\$")
                .Replace("#", "\\#")
                .Replace("%", "\\%")
                .Replace("&", "\\&")
                .Replace("_", "\\_")
                .Replace("^", "\\textasciicircum{}")
                .Replace("~", "\\textasciitilde{}");
        }

        private string FormatMarkdown(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            
            // First split by tokens we want to preserve?
            // Actually, we must escape first, then re-apply markdown formatting.
            // But wait, if text has **Foo**, Escape turns it into **Foo**.
            // Then we regex match \*\*(.*?)\*\* and replace with \textbf{$1}.
            // Correct.
            
            var escaped = Escape(text);
            
            // Bold
            escaped = Regex.Replace(escaped, @"\*\*(.+?)\*\*", "\\textbf{$1}");
            // Italic
            escaped = Regex.Replace(escaped, @"\*(.+?)\*", "\\textit{$1}"); // basic single start support
            
            return escaped;
        }
    }
}

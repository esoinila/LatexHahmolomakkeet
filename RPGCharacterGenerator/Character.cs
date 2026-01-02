
using System.Collections.Generic;

namespace RPGCharacterGenerator
{
    public class Character
    {
        public string Name { get; set; } = "";
        public string Handle { get; set; } = "";
        public string Image { get; set; } = "";
        public string Quote { get; set; } = "";
        public string Role { get; set; } = "";
        public string PersonalQuest { get; set; } = "";
        public string KeyEntity { get; set; } = "";
        public List<string> Abilities { get; set; } = new List<string>();
        public List<string> Personality { get; set; } = new List<string>();
        public List<string> StressResponse { get; set; } = new List<string>();
        public List<string> Equipment { get; set; } = new List<string>();
        public string Background { get; set; } = "";

        public string FullName => string.IsNullOrEmpty(Handle) ? Name : $"{Name} {Handle}";
    }
}

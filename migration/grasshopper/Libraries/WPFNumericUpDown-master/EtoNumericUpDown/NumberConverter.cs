using Eto.Forms;
using EtoNumericUpDown.Controls;
using System;
using System.Globalization;
using System.Text.RegularExpressions;

namespace EtoNumericUpDown
{
    public class NumberConverter<T> where T : struct, IFormattable, IComparable<T>
    {
        public static string Convert(T value, GenericNumericControl<T> control, CultureInfo culture)
        {
            // Converting to string
            string text = value.ToString(control.FormatString, culture);
            if (string.IsNullOrEmpty(control.Suffix))
                return text;
            else
                return text + " " + control.Suffix;
        }

        public static T ConvertBack(string value, GenericNumericControl<T> control, CultureInfo culture)
        {
            // Converting to T
            if (!string.IsNullOrEmpty(control.Suffix))
            {
                var t = value.GetEnumerator();
                string current = "";
                string filtered = "";
                while (t.MoveNext())
                {
                    current += t.Current;
                    if (Regex.Match(current, control.RegexPattern).Success)
                        filtered = current;
                    else
                        break;
                }
                value = filtered;
            }
            if (control.ConvertToValue(value, out T result))
                return result;
            else
                return default(T);
        }
    }
}

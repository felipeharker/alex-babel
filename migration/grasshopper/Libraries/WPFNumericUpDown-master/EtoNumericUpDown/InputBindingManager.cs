using Eto.Forms;
using System;
using System.Collections.Generic;
using System.Text;

namespace EtoNumericUpDown
{
    public static class InputBindingsManager
    {
        public static void SetUpdatePropertySourceWhenEnterPressed(Control control, Action updateSourceAction)
        {
            if (control == null) return;

            control.KeyDown += (sender, e) =>
            {
                if (e.Key == Keys.Enter)
                {
                    updateSourceAction?.Invoke();
                }
            };
        }
    }
}

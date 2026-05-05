using Eto.Drawing;
using Eto.Forms;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace EtoNumericUpDown
{
    public abstract class NumericControl : Panel
    {
        internal TextBox textBox;
        Button incBTN;
        Button decBTN;
        UITimer timer;
        Command command;

        internal abstract string RegexPattern { get; }

        public NumericControl()
        {
            textBox = new TextBox() { Font = new Font(SystemFont.Default, 10) };
            //InputBindingsManager.SetUpdatePropertySourceWhenEnterPressed(textBox, UpdateBindingSource);
            incBTN = new Button { Text = "▲", Size = new Eto.Drawing.Size(16, 14), Font = new Font(SystemFont.Default, 5) };
            decBTN = new Button { Text = "▼", Size = new Eto.Drawing.Size(16, 14) , Font = new Font(SystemFont.Default,5) };
            
            var layout = new TableLayout
            {
                Padding = new Padding(0,0,0,0),
                Spacing = new Size(0, 0),
                Rows =
                {          
                    new TableRow(
                        new TableCell(textBox, true),
                        new TableCell(new TableLayout
                        {
                            Rows =
                            {
                                new TableRow(incBTN),
                                new TableRow(decBTN)
                            }
                        }, false)
                    )
                }
            };


            Content = layout;

            incBTN.MouseDown += (sender, e) => incBTN_MouseLeftButtonDown(sender, e);
            incBTN.MouseUp += (sender, e) => incBTN_MouseLeftButtonUp(sender, e);
            decBTN.MouseDown += (sender, e) => incBTN_MouseLeftButtonDown(sender, e);
            decBTN.MouseUp += (sender, e) => incBTN_MouseLeftButtonUp(sender, e);
            textBox.TextChanging += (sender, e) => textBox_TextChanging(sender, e);

            timer = new UITimer
            {
                Interval = 0.4 // 400 ms
            };
            timer.Elapsed += Timer_Elapsed;
        }

        private void Timer_Elapsed(object sender, EventArgs e)
        {
            if (command != null && command.Enabled)
                command.Execute();
            timer.Interval = 0.1; // 100 ms
        }

        private void incBTN_MouseLeftButtonDown(object sender, MouseEventArgs e)
        {
            var btn = sender as Button;
            command = btn.Text == incBTN.Text ? IncrementCommand : DecrementCommand;
            if (command.Enabled)
                command.Execute();
            timer.Start();
        }

        private void incBTN_MouseLeftButtonUp(object sender, MouseEventArgs e)
        {
            timer.Stop();
            timer.Interval = 0.4; // 400 ms
        }

        private void textBox_TextChanging(object sender, TextChangingEventArgs e)
        {
            e.Cancel = !Regex.IsMatch(e.NewText, RegexPattern);
        }
        //private void UpdateBindingSource()
        //{
           
        //    // Logic to update the binding source, if needed.
        //}
        public abstract Command IncrementCommand { get; }
        public abstract Command DecrementCommand { get; }
    }
}

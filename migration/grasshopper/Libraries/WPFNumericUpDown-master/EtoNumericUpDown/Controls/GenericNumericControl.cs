using System;
using Eto.Forms;
using Eto.Drawing;
using System.ComponentModel;
using System.Globalization;

/*
MIT License
Copyright (c) 2021 ALI TORABI (ali@parametriczoo.com)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
namespace EtoNumericUpDown.Controls
{
    public class GenericNumericControl<T> : NumericControl where T : struct, IFormattable, IComparable<T>
    {
        // Replace DependencyProperty with normal properties and INotifyPropertyChanged
        private T _data;
        private T _minimum;
        private T _maximum;
        private T _increment;
        private int _decimals;
        private string _suffix;

        public GenericNumericControl()
        {
            Load += GenericNumericControl_Loaded;
        }

        internal override string RegexPattern
        {
            get
            {
                if (typeof(T).Equals(typeof(int)))
                {
                    return (toInt(Minimum) < 0) ? signedInteger : unSignedInteger;
                }
                else if (typeof(T).Equals(typeof(decimal)))
                {
                    return (toDecimal(Minimum) < 0) ? signedDecimal : unSignedDecimal;
                }
                else if (typeof(T).Equals(typeof(double)))
                {
                    return (toDouble(Minimum) < 0) ? signedDecimal : unSignedDecimal;
                }
                else
                {
                    return signedDecimal;
                }
            }
        }

        #region Properties
        public T DATA
        {
            get => _data;
            set
            {
                if (!_data.Equals(value))
                {
                    _data = value;
                    OnPropertyChanged(nameof(DATA));
                }
            }
        }

        public T Minimum
        {
            get => _minimum;
            set
            {
                if (!_minimum.Equals(value))
                {
                    _minimum = value;
                    OnPropertyChanged(nameof(Minimum));
                }
            }
        }

        public T Maximum
        {
            get => _maximum;
            set
            {
                if (!_maximum.Equals(value))
                {
                    _maximum = value;
                    OnPropertyChanged(nameof(Maximum));
                }
            }
        }

        public T IncrementValue
        {
            get => _increment;
            set
            {
                if (!_increment.Equals(value))
                {
                    _increment = value;
                    OnPropertyChanged(nameof(IncrementValue));
                }
            }
        }

        public int Decimals
        {
            get => _decimals;
            set
            {
                if (_decimals != value)
                {
                    _decimals = value;
                    OnPropertyChanged(nameof(Decimals));
                }
            }
        }

        public string Suffix
        {
            get => _suffix;
            set
            {
                if (_suffix != value)
                {
                    _suffix = value;
                    OnPropertyChanged(nameof(Suffix));
                }
            }
        }
        #endregion

        #region Helper Methods
        int toInt(T val) => (int)Convert.ChangeType(val, typeof(int));
        decimal toDecimal(T val) => (decimal)Convert.ChangeType(val, typeof(decimal));
        double toDouble(T val) => (double)Convert.ChangeType(val, typeof(double));
        T toT(int val) => (T)Convert.ChangeType(val, typeof(int));
        T toT(decimal val) => (T)Convert.ChangeType(val, typeof(decimal));
        T toT(double val) => (T)Convert.ChangeType(val, typeof(double));
        #endregion

        #region Internal Methods
        internal virtual T increment(T value)
        {
            if (typeof(T).Equals(typeof(int)))
            {
                return toT(toInt(value) + toInt(IncrementValue));
            }
            else if (typeof(T).Equals(typeof(decimal)))
            {
                return toT(toDecimal(value) + toDecimal(IncrementValue));
            }
            else if (typeof(T).Equals(typeof(double)))
            {
                return toT(toDouble(value) + toDouble(IncrementValue));
            }
            else
            {
                throw new Exception("T expected int, decimal, or double");
            }
        }

        internal virtual T decrement(T value)
        {
            if (typeof(T).Equals(typeof(int)))
            {
                return toT(toInt(value) - toInt(IncrementValue));
            }
            else if (typeof(T).Equals(typeof(decimal)))
            {
                return toT(toDecimal(value) - toDecimal(IncrementValue));
            }
            else if (typeof(T).Equals(typeof(double)))
            {
                return toT(toDouble(value) - toDouble(IncrementValue));
            }
            else
            {
                throw new Exception("T expected int, decimal, or double");
            }
        }

        internal virtual string FormatString
        {
            get
            {
                if (typeof(T).Equals(typeof(int)))
                {
                    return "";
                }
                else if (typeof(T).Equals(typeof(decimal)))
                {
                    return $"F{Decimals}";
                }
                else if (typeof(T).Equals(typeof(double)))
                {
                    return $"N{Decimals}";
                }
                else
                {
                    throw new Exception("T expected int, decimal, or double");
                }
            }
        }

        public virtual bool ConvertToValue(string text, out T val)
        {
            bool result = false;
            if (typeof(T).Equals(typeof(int)))
            {
                result = int.TryParse(text, out int x);
                val = toT(x);
            }
            else if (typeof(T).Equals(typeof(decimal)))
            {
                result = decimal.TryParse(text, out decimal x);
                val = toT(x);
            }
            else if (typeof(T).Equals(typeof(double)))
            {
                result = double.TryParse(text, out double x);
                val = toT(x);
            }
            else
            {
                throw new Exception("T expected int, decimal, or double");
            }
            return result;
        }
        #endregion

        #region Binding and Events
        private void GenericNumericControl_Loaded(object sender, EventArgs e)
        {
            dataBinding();
        }

        internal void dataBinding()
        {
            var textBinding = new BindableBinding<GenericNumericControl<T>, string>(
               this,
               c => NumberConverter<T>.Convert(c.DATA, c, CultureInfo.CurrentCulture),
               (c, v) => c.DATA = NumberConverter<T>.ConvertBack(v, c, CultureInfo.CurrentCulture)
           );

            textBox.TextBinding.Bind(textBinding,DualBindingMode.TwoWay);
        }
        #endregion

        #region Public Methods
        public T Increment()
        {
            T temp = increment(DATA);
            if (temp.CompareTo(Maximum) > 0)
            {
                return Maximum;
            }
            else
            {
                return temp;
            }
        }

        public T Decrement()
        {
            T temp = decrement(DATA);
            if (temp.CompareTo(Minimum) < 0)
            {
                return Minimum;
            }
            else
            {
                return temp;
            }
        }
        #endregion

        #region Command Properties
        public override Command IncrementCommand => new IncrementCommand<T>(this);
        public override Command DecrementCommand => new DecrementCommand<T>(this);
        #endregion

        #region Static Members (Regex)
        internal string signedDecimal = @"^(-?)([0-9]*)(\.?)([0-9]*)$";
        internal string unSignedDecimal = @"^[0-9]*(\.?)[0-9]*$";
        internal string signedInteger = @"^-?[0-9]+$";
        internal string unSignedInteger = @"^[0-9]+$";
        #endregion

        #region INotifyPropertyChanged Implementation
        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            // Ensure the bound control updates
            textBox.UpdateBindings(BindingUpdateMode.Destination);
        }
        #endregion
    }
}


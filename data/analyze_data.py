import pandas as pd
import os

def analyze_csv(file_path, out_file):
    with open(out_file, 'a', encoding='utf-8') as f:
        f.write(f"\nAnalyzing {file_path}...\n")
        try:
            df = pd.read_csv(file_path, nrows=10)
            cols = list(df.columns)
            f.write(f"Total columns: {len(cols)}\n")
            f.write(f"Column Names: {cols}\n")
            
            f.write("\nFirst row sample:\n")
            f.write(df.iloc[0].to_string() + "\n")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            f.write(f"\nNumeric columns count: {len(numeric_cols)}\n")
            f.write(f"Numeric columns: {numeric_cols}\n")

        except Exception as e:
            f.write(f"Error analyzing {file_path}: {e}\n")

if __name__ == "__main__":
    base_path = r"d:\Aubegine\csv_files"
    telemetry_file = os.path.join(base_path, "Copy of 54-10-EC-8C-14-69.raws.csv")
    weather_file = os.path.join(base_path, "weatherHistory.csv")
    output_file = r"d:\Aubegine\data\data_analysis_output.txt"
    
    if os.path.exists(output_file):
        os.remove(output_file)
        
    analyze_csv(telemetry_file, output_file)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n" + "="*50 + "\n")
    analyze_csv(weather_file, output_file)
    print(f"Analysis written to {output_file}")

import pandas as pd

def generate_large_contract_data(path, n_rows=10000):
    data = {}
    for i in range(1, 101):
        # Integer fields, all unique, in range 0..n_rows-1
        col = [j for j in range(n_rows)]
        data[f"field{i}"] = col
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)

if __name__ == "__main__":
    generate_large_contract_data("large_contract_data.csv", n_rows=10000)

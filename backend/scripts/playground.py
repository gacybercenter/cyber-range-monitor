from pathlib import Path


cwd = Path.cwd()
print(f'Current working directory: {cwd}')

script_dir = Path(__file__).resolve()
print(f'Script directory: {script_dir}')

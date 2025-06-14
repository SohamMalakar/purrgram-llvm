import os
from collections import defaultdict
from statistics import mean
import subprocess
import time

REPEAT = 10
BENCHMARKS = "benchmarks"

LANGS = {
    'c': '.c',
    'go': '.go',
    'python': '.py',
    'javascript': '.js',
    'julia': '.jl',
    'ruby': '.rb',
    'php': '.php',
    'purrgram': '.purr'
}


def command(lang, src, compiled_path):
    args = []

    match lang:
        case 'c':
            args = [compiled_path]
        case 'go':
            args = [compiled_path]
        case 'python':
            args = ['python3', src]
        case 'javascript':
            args = ['node', src]
        case 'julia':
            args = ['julia', src]
        case 'ruby':
            args = ['ruby', src]
        case 'php':
            args = ['php', src]
        case 'purrgram':
            args = ['purr', src]
        case _:
            raise NotImplementedError

    return args


def benchmark(cmd):
    times = []

    for i in range(REPEAT+1):  # +1 for warm up
        start = time.time()
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
        except Exception as e:
            print(f"Error running {' '.join(cmd)}: {e}")
            return

        duration = time.time() - start

        if i != 0:  # skip first run for warm up
            times.append(duration)

    return {
        "avg": mean(times),
        "min": min(times),
        "max": max(times)
    }


def compile(lang, filepath, outpath):
    args = []
    match lang:
        case 'c':
            args = ["gcc", filepath, "-O3", "-o", outpath]
        case 'go':
            args = ["go", "build", "-o", outpath, filepath]
        case _:
            return

    subprocess.run(args, check=True)
    return outpath


def main():
    program_results = defaultdict(list)

    for lang in os.listdir(BENCHMARKS):
        lang_path = os.path.join(BENCHMARKS, lang)
        if not os.path.isdir(lang_path):
            continue

        for file in os.listdir(lang_path):
            src = os.path.join(lang_path, file)
            if not os.path.isfile(src):
                continue

            stats = None

            idx = file.rfind('.')
            if idx == -1:
                continue

            file_base, ext = file[:idx], file[idx:]
            program_name = file_base.lower()
            compiled_path = os.path.join(lang_path, file_base)

            try:
                if lang in LANGS.keys() and ext == LANGS[lang]:
                    compiled_path = compile(lang, src, compiled_path)
                    stats = benchmark(command(lang, src, compiled_path))

                    if compiled_path and os.path.isfile(compiled_path):
                        os.remove(compiled_path)

                if stats:
                    program_results[program_name].append({
                        "language": lang,
                        "program": program_name,
                        "avg": stats["avg"],
                        "min": stats["min"],
                        "max": stats["max"]
                    })

            except Exception as e:
                print(f"Compilation or execution failed for {src}: {e}")

    print(program_results)


if __name__ == "__main__":
    main()

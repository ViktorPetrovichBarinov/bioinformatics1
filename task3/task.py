from flytekit import task, workflow
import subprocess

@task
def bwa_index(reference: str) -> str:
    # запускаем bwa index
    subprocess.run(['bwa', 'index', reference], check=True)
    return reference

@task
def bwa_mem(reference: str, fastq: str) -> str:
    # запускаем bwa mem и gzip
    sam_gz = 'aln-se.sam.gz'
    with open(sam_gz, 'wb') as out_file:
        p1 = subprocess.Popen(['bwa', 'mem', reference, fastq], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['gzip', '-3'], stdin=p1.stdout, stdout=out_file)
        p1.stdout.close()
        p2.communicate()
    return sam_gz

@task
def sam_to_bam(sam_file: str) -> str:
    bam_file = 'aln-se.bam'
    with open(bam_file, 'wb') as bam_out:
        subprocess.run(['samtools', 'view', '-S', '-b', sam_file], stdout=bam_out, check=True)
    return bam_file

@task
def flagstat(bam_file: str) -> str:
    flagstat_txt = 'aln-se.flagstat.txt'
    with open(flagstat_txt, 'w') as flag_out:
        subprocess.run(['samtools', 'flagstat', bam_file], stdout=flag_out, check=True)
    return flagstat_txt

@task
def run_script(flagstat_file: str) -> str:
    # запускаем скрипт с параметром flagstat_file
    result = subprocess.run(['./script.sh', flagstat_file], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"script.sh failed: {result.stderr}")
    return result.stdout

@workflow
def bioinformatics_workflow(reference: str, fastq: str) -> str:
    bwa_index(reference)
    sam_gz = bwa_mem(reference, fastq)
    # распакуем sam из sam.gz для следующей задачи
    sam_file = 'aln-se.sam'
    subprocess.run(['gzip', '-d', '-c', sam_gz], stdout=open(sam_file, 'wb'), check=True)
    bam_file = sam_to_bam(sam_file)
    flagstat_file = flagstat(bam_file)
    result = run_script(flagstat_file)
    return result


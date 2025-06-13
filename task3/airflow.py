from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

AIRFLOW_HOME = '/home/ruslan/airflow'

with DAG(
    'alignment_analysis',
    start_date=datetime(2025, 1, 1),
    schedule="@once"
) as dag:
    
    index = BashOperator(
        task_id='index',
        bash_command=f'bwa index {AIRFLOW_HOME}/data/GCF_000005845.2_ASM584v2_genomic.fna'
    )

    mem = BashOperator(
        task_id='mem',
        bash_command=f'bwa mem {AIRFLOW_HOME}/data/GCF_000005845.2_ASM584v2_genomic.fna {AIRFLOW_HOME}/data/SRR33602302.fastq.gz | gzip -3 > {AIRFLOW_HOME}/data/aln-se.sam.gz'
    )
    
    unzip = BashOperator(
        task_id='unzip',
        bash_command=f'gzip -dk {AIRFLOW_HOME}/data/aln-se.sam.gz'
    )

    sam_to_bam = BashOperator(
        task_id='sam_to_bam',
        bash_command=f'samtools view -S -b {AIRFLOW_HOME}/data/aln-se.sam > {AIRFLOW_HOME}/data/aln-se.bam'
    )
    
    get_res = BashOperator(
        task_id='get_res',
        bash_command=f'samtools flagstat {AIRFLOW_HOME}/data/aln-se.bam > {AIRFLOW_HOME}/data/aln-se.flagstat.txt'
    )

    index >> mem >> unzip >> sam_to_bam >> get_res

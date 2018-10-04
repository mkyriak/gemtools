import sys
import os
import __main__ as main
import argparse
import ast
import pandas as pd
import pysam
import numpy as np
import vcf


def get_phased_basic(inputvcf='None',outpre='out',**kwargs):

	if 'vcf' in kwargs:
		inputvcf = kwargs['vcf']
	if 'out' in kwargs:
		outpre = kwargs['out']

	vcf_reader = vcf.Reader(open(inputvcf,'r'))

	sample_list = vcf_reader.samples
	cur_sample = sample_list[0]

	vcf_data=[]
	for record in vcf_reader:
		chr = record.CHROM
		pos = record.POS
		ref_allele = record.REF
		alt_allele = record.ALT
		geno = record.genotype(cur_sample)['GT']
		
		allele_list = list(ref_allele) + alt_allele
		num_alts = len(alt_allele)
		format_field=(record.FORMAT).split(":")
		
		if 'PS' in format_field:
			block_id=record.genotype(cur_sample)['PS']
		else:
			block_id="n/a"

		if '|' in geno:
			phase_status = 'phased'
			allele_1 = int(geno.split("|")[0])
			allele_2 = int(geno.split("|")[1])
		else:
			phase_status = 'not_phased'
			allele_1 = int(geno.split("/")[0])
			allele_2 = int(geno.split("/")[1])
			
		if str(allele_1)==str(allele_2):
			num_alleles = 1
			hom_status = "hom"
		else:
			num_alleles = 2
			hom_status = "het"
		
		if record.is_snp:
			var_type = "snv"
		else:
			var_type = "indel"

		if ('BX' in format_field and str(allele_1).isdigit() == True and str(allele_2).isdigit() == True):
			bc1=record.genotype(cur_sample)['BX'][int(allele_1)]
			bc2=record.genotype(cur_sample)['BX'][int(allele_2)]
			if bc1=='':
				bc1="n/a"	
				bc1_ct=0
			else:
				bc1_ct=len(bc1.split(";"))
			if bc2=='':
				bc2="n/a"
				bc2_ct=0
			else:
				bc2_ct=len(bc2.split(";"))

		else:
			bc1,bc2,bc1_ct,bc2_ct="n/a"

		vcf_data.append((chr,pos,ref_allele,alt_allele,geno,allele_list,num_alts,block_id,phase_status,allele_1,allele_2,num_alleles,hom_status,var_type,bc1,bc1_ct,bc2,bc2_ct))

	df=pd.DataFrame(vcf_data)
	df.columns=['chrom','pos','ref','alt','gt','allele_list','num_alts','block_id','phase_status','allele_1','allele_2','num_alleles','hom_status','var_type','bc1','bc1_ct','bc2','bc2_ct']

	df.to_csv(str(outpre), sep="\t", index=False, header=False)

	return df
#!/bin/bash

cd /path/to/your/folder/

of1="name_of_the_summary_file.txt"
inf="/path/to/text/of/sampleIDs.txt"


hv="Sample	snp_coverage_mqc-generalstats-snp_coverage-Covered_Snps	snp_coverage_mqc-generalstats-snp_coverage-Total_Snps	Samtools_Flagstat_(pre-samtools_filter)_mqc-generalstats-samtools_flagstat_pre_samtools_filter-flagstat_total	Samtools_Flagstat_(pre-samtools_filter)_mqc-generalstats-samtools_flagstat_pre_samtools_filter-mapped_passed	Samtools_Flagstat_(post-samtools_filter)_mqc-generalstats-samtools_flagstat_post_samtools_filter-flagstat_total	endorSpy_mqc-generalstats-endorspy-endogenous_dna	Samtools_Flagstat_(post-samtools_filter)_mqc-generalstats-samtools_flagstat_post_samtools_filter-mapped_passed	endorSpy_mqc-generalstats-endorspy-endogenous_dna_post	Picard_mqc-generalstats-picard-PERCENT_DUPLICATION	DamageProfiler_mqc-generalstats-damageprofiler-5_Prime1	DamageProfiler_mqc-generalstats-damageprofiler-5_Prime2	DamageProfiler_mqc-generalstats-damageprofiler-3_Prime1	DamageProfiler_mqc-generalstats-damageprofiler-3_Prime2	DamageProfiler_mqc-generalstats-damageprofiler-mean_readlength	DamageProfiler_mqc-generalstats-damageprofiler-median	mtnucratio_mqc-generalstats-mtnucratio-mtreads	mtnucratio_mqc-generalstats-mtnucratio-mt_cov_avg	mtnucratio_mqc-generalstats-mtnucratio-mt_nuc_ratio	QualiMap_mqc-generalstats-qualimap-mapped_reads	QualiMap_mqc-generalstats-qualimap-mean_coverage	QualiMap_mqc-generalstats-qualimap-median_coverage	QualiMap_mqc-generalstats-qualimap-1_x_pc	QualiMap_mqc-generalstats-qualimap-2_x_pc	QualiMap_mqc-generalstats-qualimap-3_x_pc	QualiMap_mqc-generalstats-qualimap-4_x_pc	QualiMap_mqc-generalstats-qualimap-5_x_pc	QualiMap_mqc-generalstats-qualimap-avg_gc	DamageProfiler_mqc-generalstats-damageprofiler-std	mtnucratio_mqc-generalstats-mtnucratio-nuc_cov_avg	mtnucratio_mqc-generalstats-mtnucratio-nucreads	QualiMap_mqc-generalstats-qualimap-percentage_aligned	QualiMap_mqc-generalstats-qualimap-total_reads	QualiMap_mqc-generalstats-qualimap-general_error_rate	SexDetErrmine_mqc-generalstats-sexdeterrmine-RateErrX	SexDetErrmine_mqc-generalstats-sexdeterrmine-RateErrY	SexDetErrmine_mqc-generalstats-sexdeterrmine-RateX	SexDetErrmine_mqc-generalstats-sexdeterrmine-RateY	nuclear_contamination_mqc-generalstats-nuclear_contamination-Num_SNPs	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_estimate	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_SE	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_estimate	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_SE	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_estimate	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_SE	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_estimate	nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_SE"
echo ${hv} > ${of1}
for P in $(cat $inf); do 
    tfn1="/mnt/archgen/Autorun_eager/eager_outputs(_old)/TF/*/"${P}"/multiqc/multiqc_data/multiqc_general_stats.txt"
    X=($(cat ${tfn1} | tail -1 | awk '{print $1":"}' ))  
    Y=($(cat ${tfn1} | head -2 | tail -1 | awk '{print $2":"$3":"}')) 
    Z=($(cat ${tfn1} | tail -1 | awk '{print $2":"$3":"$4":"$5":"$6":"$7":"$8":"$9":"$10":"$11":"$12":"$13":"$14":"$15":"$16":"$17":"$18":"$19":"$20":"$21":"$22":"$23":"$24":"$25":"$26":"$27":"$28":"$29":"$30":"$31":"$32":"$33":"$34":"$35":"$36":"$37":"$38":"$39":"$40":"$41":"$42":"$43":"$44":"$45":"$46":"$47":"$48}')) 
    echo ${X}${Y}${Z} | sed s/":"/" "/g >> ${of1}
    echo ${P}" is processed" 
done

#!/usr/bin/env python3
import json
import argparse
import sys
import os

VERSION = "1.3.0"


def get_individual_library_stats(mqc_data):
    ## Read json file, and combine relevant sample and library stats into a dictionary
    with open(mqc_data, "r") as json_file:
        data = json.load(json_file)
    ## Create empty dicts and lists to store results
    results = {}
    sample_stats = {}
    library_stats = {}
    sample_libraries = []
    ## Loop through json file and store relevant stats in dicts
    for key in data["report_saved_raw_data"]["multiqc_general_stats"].keys():
        ## If the key contains a '.', it is a library stat, otherwise it is a sample stat
        if len(key.split(".")) > 1:
            ## eager 2.5.0 also has split by UDG for some stats. we want to compile these together, as each library can only have one udg treatment.
            ## By splitting by '_udg', we can get the library ID, and then add the attributes to the library dict for both cases.
            try:
                ## If the library key is already in the dict, add the attributes to it
                library_stats[key.split("_udg")[0]].update(
                    data["report_saved_raw_data"]["multiqc_general_stats"][key]
                )
            except KeyError:
                ## If the library ID doesn't exist in the dict, create it
                library_stats[key.split("_udg")[0]] = data["report_saved_raw_data"][
                    "multiqc_general_stats"
                ][key]
                sample_libraries.append(
                    key
                )  ## Keep track of library IDs for later. Only add it if its new.
            ## Not actually needed since key.split("_udg")[0] will always be the Library_ID
            # else:
            #     ## Library key is actual Library_ID
            #     try:
            #         ## If the library key is already in the dict, add the attributes to it
            #         library_stats[key].update(data["report_saved_raw_data"]["multiqc_general_stats"][key])
            #     except KeyError:
            #         ## If the library ID doesn't exist in the dict, create it
            #         library_stats[key] = data["report_saved_raw_data"]["multiqc_general_stats"][key]
            #     sample_libraries.append(key)  ## Keep track of library IDs for later
        else:
            sample_stats[key] = data["report_saved_raw_data"]["multiqc_general_stats"][
                key
            ]

    for library in sample_libraries:
        ## Get the sample ID from the library ID, to ensure ss libs get ss sample stats
        ## Use update instead of union to work with python <3.9
        compiled_results = {}
        compiled_results.update(sample_stats[library.split(".")[0]])
        compiled_results.update(library_stats[library])
        results[library] = compiled_results
        ## Old implementation using dict union.
        ## Use union of attributes to combine dicts. attributes from the library level will overwrite any that exist in the sample level. Should be no overlap, but good to note.
        # results[library] = dict(sample_stats[library.split('.')[0]] | library_stats[library])

    ## Standardise column naming across multiqc versions
    results = standardise_column_names(results)
    ## results is a dict of dicts, with the library ID as the key. The value then contains a dict of the combined stats for that library/sample.
    return results


## Some column names changed from 2.4.5 to 2.5.0, so we need to standardise the names of these columns across both versions.
def standardise_column_names(collected_stats):
    #    OLD NAME                                                                               NEW NAME
    #    DamageProfiler_mqc-generalstats-damageprofiler-3_Prime1                                mapDamage_mqc-generalstats-mapdamage-mapdamage_3_Prime1
    #    DamageProfiler_mqc-generalstats-damageprofiler-3_Prime2                                mapDamage_mqc-generalstats-mapdamage-mapdamage_3_Prime2
    #    DamageProfiler_mqc-generalstats-damageprofiler-5_Prime1                                mapDamage_mqc-generalstats-mapdamage-mapdamage_5_Prime1
    #    DamageProfiler_mqc-generalstats-damageprofiler-5_Prime2                                mapDamage_mqc-generalstats-mapdamage-mapdamage_5_Prime2
    #    DamageProfiler_mqc-generalstats-damageprofiler-mean_readlength                         NA
    #    DamageProfiler_mqc-generalstats-damageprofiler-median                                  NA
    #    DamageProfiler_mqc-generalstats-damageprofiler-std                                     NA
    #    endorSpy_mqc-generalstats-endorspy-endogenous_dna                                      base endorSpy_mqc-generalstats-base_endorspy-endogenous_dna
    #    endorSpy_mqc-generalstats-endorspy-endogenous_dna_post                                 base endorSpy_mqc-generalstats-base_endorspy-endogenous_dna_post
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_SE             base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_ML_SE
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_estimate       base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_ML_estimate
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_SE            base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_MOM_SE
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_estimate      base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_MOM_estimate
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_SE             base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_ML_SE
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_estimate       base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_ML_estimate
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_SE            base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_MOM_SE
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_estimate      base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_MOM_estimate
    #    nuclear_contamination_mqc-generalstats-nuclear_contamination-Num_SNPs                  base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Num_SNPs
    #    snp_coverage_mqc-generalstats-snp_coverage-Covered_Snps                                base snp_coverage_mqc-generalstats-base_snp_coverage-Covered_Snps
    #    snp_coverage_mqc-generalstats-snp_coverage-Total_Snps                                  base snp_coverage_mqc-generalstats-base_snp_coverage-Total_Snps
    new_attributes = {
        "dmg_3p_1": "N/A",
        "dmg_3p_2": "N/A",
        "dmg_5p_1": "N/A",
        "dmg_5p_2": "N/A",
        "mean_read_length": "N/A",
        "median_read_length": "N/A",
        "read_length_std_dev": "N/A",
        "endogenous": "N/A",
        "endogenous_post": "N/A",
        "nuc_cont_m1_ml_se": "N/A",
        "nuc_cont_m1_ml_est": "N/A",
        "nuc_cont_m1_mom_se": "N/A",
        "nuc_cont_m1_mom_est": "N/A",
        "nuc_cont_m2_ml_se": "N/A",
        "nuc_cont_m2_ml_est": "N/A",
        "nuc_cont_m2_mom_se": "N/A",
        "nuc_cont_m2_mom_est": "N/A",
        "nuc_cont_snps": "N/A",
        "snps_covered": "N/A",
        "snps_total": "N/A",
    }

    old_names = {
        "dmg_3p_1": "DamageProfiler_mqc-generalstats-damageprofiler-3_Prime1",
        "dmg_3p_2": "DamageProfiler_mqc-generalstats-damageprofiler-3_Prime2",
        "dmg_5p_1": "DamageProfiler_mqc-generalstats-damageprofiler-5_Prime1",
        "dmg_5p_2": "DamageProfiler_mqc-generalstats-damageprofiler-5_Prime2",
        "mean_read_length": "DamageProfiler_mqc-generalstats-damageprofiler-mean_readlength",
        "median_read_length": "DamageProfiler_mqc-generalstats-damageprofiler-median",
        "read_length_std_dev": "DamageProfiler_mqc-generalstats-damageprofiler-std",
        "endogenous": "endorSpy_mqc-generalstats-endorspy-endogenous_dna",
        "endogenous_post": "endorSpy_mqc-generalstats-endorspy-endogenous_dna_post",
        "nuc_cont_m1_ml_se": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_SE",
        "nuc_cont_m1_ml_est": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_ML_estimate",
        "nuc_cont_m1_mom_se": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_SE",
        "nuc_cont_m1_mom_est": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method1_MOM_estimate",
        "nuc_cont_m2_ml_se": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_SE",
        "nuc_cont_m2_ml_est": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_ML_estimate",
        "nuc_cont_m2_mom_se": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_SE",
        "nuc_cont_m2_mom_est": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Method2_MOM_estimate",
        "nuc_cont_snps": "nuclear_contamination_mqc-generalstats-nuclear_contamination-Num_SNPs",
        "snps_covered": "snp_coverage_mqc-generalstats-snp_coverage-Covered_Snps",
        "snps_total": "snp_coverage_mqc-generalstats-snp_coverage-Total_Snps",
    }

    new_names = {
        "dmg_3p_1": "mapDamage_mqc-generalstats-mapdamage-mapdamage_3_Prime1",
        "dmg_3p_2": "mapDamage_mqc-generalstats-mapdamage-mapdamage_3_Prime2",
        "dmg_5p_1": "mapDamage_mqc-generalstats-mapdamage-mapdamage_5_Prime1",
        "dmg_5p_2": "mapDamage_mqc-generalstats-mapdamage-mapdamage_5_Prime2",
        "endogenous": "base endorSpy_mqc-generalstats-base_endorspy-endogenous_dna",
        "endogenous_post": "base endorSpy_mqc-generalstats-base_endorspy-endogenous_dna_post",
        "nuc_cont_m1_ml_se": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_ML_SE",
        "nuc_cont_m1_ml_est": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_ML_estimate",
        "nuc_cont_m1_mom_se": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_MOM_SE",
        "nuc_cont_m1_mom_est": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method1_MOM_estimate",
        "nuc_cont_m2_ml_se": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_ML_SE",
        "nuc_cont_m2_ml_est": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_ML_estimate",
        "nuc_cont_m2_mom_se": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_MOM_SE",
        "nuc_cont_m2_mom_est": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Method2_MOM_estimate",
        "nuc_cont_snps": "base nuclear_contamination_mqc-generalstats-base_nuclear_contamination-Num_SNPs",
        "snps_covered": "base snp_coverage_mqc-generalstats-base_snp_coverage-Covered_Snps",
        "snps_total": "base snp_coverage_mqc-generalstats-base_snp_coverage-Total_Snps",
    }

    ## Starting with all NAs, add in any values that exist in either the old dict or the new dict
    for library in collected_stats:
        new_stats = collected_stats[library]
        new_stats.update(new_attributes)  ## Add all new attributed with NAs
        ## Deal with older versions of multiqc
        try:
            for name, old_name in old_names.items():
                new_stats[name] = new_stats[old_name]
        except KeyError:
            pass
        ## Deal with newer versions of multiqc
        try:
            for name, new_name in new_names.items():
                new_stats[name] = new_stats[new_name]
        except KeyError:
            pass
        # print("library:", library, "stats", new_stats, sep="\n")
        collected_stats[library] = new_stats
    return collected_stats


def timestamp_diff_in_sec(file1, file2):
    ## Get the creation time of each file
    for f in [file1, file2]:
        ## Check that the files indeed exist
        if not os.path.exists(f) or not os.path.isfile(f):
            print(
                f"Required file {f} not found! Results for this sample might be corrupted.",
                file=sys.stderr,
            )
            return 1_000_000  ## Return a large number to indicate that the files are missing

    timestamp1 = os.path.getmtime(file1)
    timestamp2 = os.path.getmtime(file2)

    ## Return the modification time difference in seconds
    return abs(timestamp1 - timestamp2)


def files_are_consistent(mqc_data, mqc_html, skip_check=False):
    ## Check if the multiqc data and html files are up to date
    ## Complain if the difference is more than 1 minute (should be less than a second, but give some leeway for network/filesystem latency etc.)
    if timestamp_diff_in_sec(mqc_data, mqc_html) > 60:
        return skip_check
    return True

def read_eager_input_table(file_path):
    '''
    Creates dictionaries with all the possible combinations of the columns in the given file.
    '''
    l = file_path.readlines()
    headers = l[0].strip().split('\t')
    return map(lambda row: dict(zip(headers, row.split('\t'))), l[1:])

import glob

def dict_data(path='./', columns=[]):
    '''
    Asks for input from the user. The input should be a directory for a folder and any number of the words from 
        the allowed_word list.
    
    A \\*.tsv is always added automatically at the end of the given directory, so that only .tsv files 
        will be searched for, but it should also be taken into consideration when providing the directory 
        for the folder by the user.
    
    All of the .tsv files in the folder are read.

    This function calls the function above to create a dictionary out of the .tsv files of the given folder 
        and then prints a list with all the requested dictionaries (could be just one or could be multiple).

    The requested dictionary will always have as keys the data from the Library_ID column of the .tsv files 
        and as correspoding values the data of the column which titled with the word provided by the user
        (one of the words in the allowed_word list).

    If the user provides multiple words, a dictionary will be created for each of the corresponding columns.
    '''
    allowed_words = {"Sample_Name", "Lane", "Colour_Chemistry", "SeqType", "Organism", "Strandedness", 
                        "UDG_Treatment", "R1", "R2", "BAM"}
    if all(word in allowed_words for word in columns):
        pattern = path + '*.tsv'
        p = glob.glob(pattern)
        print(pattern) # Prints the whole of the provided pattern. Helpful to identify a problem caused by problematic directory input
        asked_dict = {}
        if not p:
            print("No .tsv files found in the specified folder.") # Returns an error message if there is an issue with the creation of p
            return
        
        asked_dict = [{} for _ in columns]  # Create a list of empty dictionaries for each requested column
        for file_path in p:
            with open(file_path, 'r') as f: 
                    for row in read_eager_input_table(f): # Calls the above function
                        if "Library_ID" in row: # This part could be skipped but eh, whatever
                            key = row["Library_ID"]
                            for idx, col in enumerate(columns):
                                asked_dict[idx][key] = row[col]
                            
        print(asked_dict)

def main():
    ## Column order same as old script.
    output_columns = {
        "Covered_SNPs_on_1240K": "snps_covered",
        "Total_SNPs_on_1240K": "snps_total",
        "Nr_of_input_reads": "Samtools Flagstat (pre-samtools filter)_mqc-generalstats-samtools_flagstat_pre_samtools_filter-flagstat_total",
        "Nr_of_mapped_reads": "Samtools Flagstat (pre-samtools filter)_mqc-generalstats-samtools_flagstat_pre_samtools_filter-mapped_passed",
        "Nr_of_input_reads_over_30bp": "Samtools Flagstat (post-samtools filter)_mqc-generalstats-samtools_flagstat_post_samtools_filter-flagstat_total",
        "%_Endogenous_DNA": "endogenous",
        "Nr_of_mapped_reads_over_30bp": "Samtools Flagstat (post-samtools filter)_mqc-generalstats-samtools_flagstat_post_samtools_filter-mapped_passed",
        "%_Endogenous_DNA_over_30bp": "endogenous_post",
        "Proportion_of_duplicate_reads": "Picard_mqc-generalstats-picard-PERCENT_DUPLICATION",
        "Damage_5'_bp1": "dmg_5p_1",
        "Damage_5'_bp2": "dmg_5p_2",
        "Damage_3'_bp1": "dmg_3p_1",
        "Damage_3'_bp2": "dmg_3p_2",
        "Mean_read_length": "mean_read_length",
        "Median_read_length": "median_read_length",
        "Nr_mtDNA_reads": "mtnucratio_mqc-generalstats-mtnucratio-mtreads",
        "Mean_mt_coverage": "mtnucratio_mqc-generalstats-mtnucratio-mt_cov_avg",
        "mt_to_nuclear_read_ratio": "mtnucratio_mqc-generalstats-mtnucratio-mt_nuc_ratio",
        "Nr_of_unique_mapped_reads": "QualiMap_mqc-generalstats-qualimap-mapped_reads",
        "Mean_fold_coverage": "QualiMap_mqc-generalstats-qualimap-mean_coverage",
        "Median_fold_coverage": "QualiMap_mqc-generalstats-qualimap-median_coverage",
        "%_of_genome_covered_by_at_least_1_read": "QualiMap_mqc-generalstats-qualimap-1_x_pc",
        "%_of_genome_covered_by_at_least_2_reads": "QualiMap_mqc-generalstats-qualimap-2_x_pc",
        "%_of_genome_covered_by_at_least_3_reads": "QualiMap_mqc-generalstats-qualimap-3_x_pc",
        "%_of_genome_covered_by_at_least_4_reads": "QualiMap_mqc-generalstats-qualimap-4_x_pc",
        "%_of_genome_covered_by_at_least_5_reads": "QualiMap_mqc-generalstats-qualimap-5_x_pc",
        "%_GC_of_unique_reads": "QualiMap_mqc-generalstats-qualimap-avg_gc",
        "Read_length_std_dev": "read_length_std_dev",
        "Mean_fold_coverage_on_nuclear_genome": "mtnucratio_mqc-generalstats-mtnucratio-nuc_cov_avg",
        "Nr_nuclearDNA_reads": "mtnucratio_mqc-generalstats-mtnucratio-nucreads",
        # "%_of_mapped_reads": "QualiMap_mqc-generalstats-qualimap-percentage_aligned",
        "Nr_of_reads_total": "QualiMap_mqc-generalstats-qualimap-total_reads",
        "Qualimap_General_error_rate": "QualiMap_mqc-generalstats-qualimap-general_error_rate",
        "StdErr_of_X_relative_coverage": "SexDetErrmine_mqc-generalstats-sexdeterrmine-RateErrX",
        "StdErr_of_Y_relative_coverage": "SexDetErrmine_mqc-generalstats-sexdeterrmine-RateErrY",
        "Relative_coverage_on_X_chromosome": "SexDetErrmine_mqc-generalstats-sexdeterrmine-RateX",
        "Relative_coverage_on_Y_chromosome": "SexDetErrmine_mqc-generalstats-sexdeterrmine-RateY",
        "Nr_SNPs_used_in_contamination_estimation": "nuc_cont_snps",
        "Nuclear_contamination_M1_ML": "nuc_cont_m1_ml_est",
        "Nuclear_contamination_M1_ML_Error": "nuc_cont_m1_ml_se",
        "Nuclear_contamination_M1_MOM": "nuc_cont_m1_mom_est",
        "Nuclear_contamination_M1_MOM_Error": "nuc_cont_m1_mom_se",
        "Nuclear_contamination_M2_ML": "nuc_cont_m2_ml_est",
        "Nuclear_contamination_M2_ML_Error": "nuc_cont_m2_ml_se",
        "Nuclear_contamination_M2_MOM": "nuc_cont_m2_mom_est",
        "Nuclear_contamination_M2_MOM_Error": "nuc_cont_m2_mom_se",
    }

    parser = argparse.ArgumentParser(
        description="This is a script for collecting a batch of library-level multiqc stats for individuals for which capture or shotgun data exists."
    )
    parser.add_argument(
        "-r",
        "--root_output_path",
        help="The root directory where the eager output lies. Within this directory there should be the structure <analysis_type>/<site_id>/<individual_id>/*.",
        required=False,
        default="/mnt/archgen/Autorun_eager/eager_outputs/",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input file with a list of individuals for which capture or shotgun data exists.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file with a list of individuals for which capture or shotgun data exists.",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--analysis_type",
        help="Analysis type: capture or shotgun. Options are: SG, TF, RP, RM. Defaults to TF.",
        default="TF",
        choices=["SG", "TF", "RP", "RM"],
    )
    parser.add_argument(
        "--skip_check",
        help="By default, results from runs where the consistency of the MultiQC output files cannot be verified will be skipped. Use this flag to disable this behaviour. Only recommended if you know why the check failed to begin with.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-H",
        "--header",
        help="Use human-readable header, instead of original MultiQC table header.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {}".format(VERSION),
        help="Print the version and exit.",
    )
    args = parser.parse_args()

    ## Print version info to stderr on runtime
    print("## {}: {}".format(parser.prog, VERSION), file=sys.stderr)

    ## Loudly declare when the script is run with the --skip_check flag
    if args.skip_check:
        print(
            "WARNING: Skipping the check for consistency between MultiQC data and report files. This may result in the inclusion of outdated results, or runtime errors!",
            file=sys.stderr,
        )

    ## Read in list of individuals
    with open(args.input, "r") as f:
        individuals = f.read().splitlines()
        print(
            "Found {} individuals in input file.".format(len(individuals)), file=sys.stderr
        )

    ## Iterate over individuals and collect stats
    collected_stats = {}
    skip_count = 0
    for ind in individuals:
        ## Set input file path
        mqc_data = "{}/{}/{}/{}/multiqc/multiqc_data/multiqc_data.json".format(
            args.root_output_path, args.analysis_type, ind[0:3], ind
        )

        ## Infer path to MQC report
        report_path = mqc_data.replace(
            "multiqc_data/multiqc_data.json", "multiqc_report.html"
        )

        ## Get stats
        try:
            ## First, ensure the MQC data are consistent with the report
            if files_are_consistent(mqc_data, report_path, args.skip_check):
                collected_stats.update(get_individual_library_stats(mqc_data))
            else:
                print(
                    f"WARNING: There is a large difference in the creation time between the MultiQC data file '{mqc_data}' and the corresponding HTML '{report_path}'. Skipping.",
                    file=sys.stderr,
                )
                skip_count += 1
                continue
        except FileNotFoundError:
            print(
                "No multiqc data found for individual {}. Skipping.".format(ind),
                file=sys.stderr,
            )
            skip_count += 1
            continue
        print("Collected stats for individual {}.".format(ind), file=sys.stderr)

    ## Print number of skipped individuals to stderr if any
    if skip_count > 0:
        print(
            "WARNING: No data was found for {} individuals!".format(skip_count),
            file=sys.stderr,
        )

    ## Print results to output file
    with open(args.output, "w") as f:
        ## Add header
        if args.header:
            print("Sample", *output_columns.keys(), sep="\t", file=f)
        else:
            print("Sample", *output_columns.values(), sep="\t", file=f)
        ## Add data
        for library in sorted(collected_stats.keys()):
            try:
                print(
                    library,
                    *[
                        collected_stats[library][column]
                        for column in output_columns.values()
                    ],
                    sep="\t",
                    file=f,
                )
            except KeyError as e:
                raise Exception(
                    f"Encountered an error while trying to print stats for library: {library}."
                ) from e

        ## Add footer with version info
        flags = ""
        if args.skip_check:
            flags += " --skip_check"
        if args.header:
            flags += " --header"

        print(f"## {parser.prog}: {VERSION}", file=f)
        print(
            f"## Command: {parser.prog} -i {args.input} -o {args.output} -a {args.analysis_type}{flags}",
            file=f,
        )

if __name__ == "__main__":
    main()

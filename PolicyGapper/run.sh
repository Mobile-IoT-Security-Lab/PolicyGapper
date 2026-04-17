#!/usr/bin/env bash
export GEMINI_API_KEY=${GEMINI_API_KEY:-"default-key"}  
set -euo pipefail


AppIdFolder="/app/PolicyGapper/input" 
if [ ! -d "$AppIdFolder" ]; then
    echo "Error: The folder '$AppIdFolder' was not found."
    exit 1
fi

for categoryFile in "$AppIdFolder"/*.txt; do
    if [ ! -f "$categoryFile" ]; then
        echo "No .txt files found in folder '$AppIdFolder'."
        break
    fi

    echo "--------------------------------------------------"
    echo "PIPELINE START for the file:: $categoryFile"
    echo "--------------------------------------------------"

    file_start=$(date +%s.%N)

    while IFS= read -r category_line || [ -n "$category_line" ]; do
        if [ -z "$category_line" ]; then
            continue
        fi

        echo "Processing PackageName: $category_line"
        # ####################################################################################
        #                                 #SCRAPING DDS AND PPP#
        # ####################################################################################

        node ./google-play-scraper/ScraperDSS.js "$category_line" || {
            echo "Error in LLMScraperDDS.py for $category_line — skip."
            continue
        }
        python3 ./Utils/ScraperPPP.py "$category_line" || {
            echo "Error in LLMScraperPPP.py for $category_line — skip."
            continue
        }
        # # ####################################################################################
        # #                                 #PRE PROCESSING#
        # # ####################################################################################
        # python3 ./LLMPreAnalysisScripts/PreAnalysisCollection.py "$category_line" || {
        #     echo "Error in LLMPreAnalyzeCollectionPPP.py for $category_line — skip."
        # }

        # python3 ./LLMPreAnalysisScripts/PreAnalysisShare.py "$category_line" || {
        #     echo "Error in LLMPreAnalyzeSharePPP.py for $category_line — skip."
        # }

        # # ####################################################################################
        # #                                 #MAIN ANALYSIS#
        # # ####################################################################################
        # python3 ./LLMAnalysisScripts/3Group/Collection/CollectionDeviceData.py "$category_line" || {
        #     echo "Error in LLMAnalyzeCollectionPPP.py for $category_line — skip."
        # }
        # python3 ./LLMAnalysisScripts/3Group/Collection/CollectionPersonalInfo.py "$category_line" || {
        #     echo "Error in LLMAnalyzeCollectionPPP.py for $category_line — skip."
        # }
        # python3 ./LLMAnalysisScripts/3Group/Collection/CollectionUserGeneratedData.py "$category_line" || {
        #     echo "Error in LLMAnalyzeCollectionPPP.py for $category_line — skip."
        # }

        # python3 ./LLMAnalysisScripts/3Group/Share/ShareDeviceData.py "$category_line" || {
        #     echo "Error in LLMAnalyzeSharePPP.py for $category_line — skip."
        # }

        # python3 ./LLMAnalysisScripts/3Group/Share/SharePersonalInfo.py "$category_line" || {
        #     echo "Error in LLMAnalyzeSharePPP.py for $category_line — skip."
        # }
        
        # python3 ./LLMAnalysisScripts/3Group/Share/ShareUserGeneratedData.py "$category_line" || {
        #     echo "Error in LLMAnalyzeSharePPP.py for $category_line — skip."
        # }
        
        # # ####################################################################################
        # #                                 #ADJUST RESULTS#
        # # ####################################################################################
        # python3 ./Utils/adjustFilesCollection.py "$category_line"_CollectionDeviceData
        # python3 ./Utils/adjustFilesCollection.py "$category_line"_CollectionPersonalInfo
        # python3 ./Utils/adjustFilesCollection.py "$category_line"_CollectionUserGeneratedData
        
        # python3 ./Utils/adjustFilesShare.py "$category_line"_ShareDeviceData
        # python3 ./Utils/adjustFilesShare.py "$category_line"_SharePersonalInfo
        # python3 ./Utils/adjustFilesShare.py "$category_line"_ShareUserGeneratedData

        # python3 ./Utils/mergeResultsCollection.py "$category_line"_CollectionDeviceData.json "$category_line"_CollectionPersonalInfo.json "$category_line"_CollectionUserGeneratedData.json
        # python3 ./Utils/mergeResultsShare.py "$category_line"_ShareDeviceData.json "$category_line"_SharePersonalInfo.json "$category_line"_ShareUserGeneratedData.json

        # # ####################################################################################
        # #                                 #POST PROCESSING#
        # # ####################################################################################
        # echo "Analysis Post Processing Collection Results"
        # python3 ./LLMPostAnalysisScipts/PostAnalysisCollection.py "$category_line"
        
        # echo "Analysis Post Processing Share Results"
        # python3 ./LLMPostAnalysisScipts/PostAnalysisShare.py "$category_line"

        # echo "Pipeline completed for: $category_line"
        # echo ""

    done < "$categoryFile"

    file_end=$(date +%s.%N)
    elapsed=$(echo "$file_end - $file_start" | bc -l)
    printf "Total time for file %s: %.2f seconds\n" "$categoryFile" "$elapsed"
    rm -rf ./UrlPrivacyPolicy.txt
    echo "--------------------------------------------------"
    echo "PIPELINE FINISHED for file: $categoryFile"
    echo "--------------------------------------------------"
done

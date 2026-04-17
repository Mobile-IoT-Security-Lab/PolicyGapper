import dss from './lib/datasafety.js';
import fs from 'fs/promises';
import app from './lib/app.js';

/**
 * @param {string} filePath 
 * @returns {Promise<string[]>} 
 */

async function main() {
    const packageName = process.argv[2];
    if (!packageName) {
        console.error("Please specify the path to the file containing the packageName as an argument.");
        return;
    }


    console.log(`Process packageName: ${packageName}`);
    try {
        app({ appId: packageName }).then(async data => {
            const privacyPolicyUrl = data.privacyPolicy;
            if (privacyPolicyUrl) {
                console.log(`Privacy Policy URL found: ${privacyPolicyUrl}`);
                await fs.writeFile(`UrlPrivacyPolicy.txt`, privacyPolicyUrl);
            } else {
                console.log('Privacy Policy URL not found for this app.');
            }
        })
            .catch(err => console.error(`Failed:`, err));


        dss({ appId: packageName }).then(async data => {
            return await fs.writeFile(`/app/DSS/${packageName}.json`, JSON.stringify(data, null, 2));

        })
            .catch(err => console.error(`Failed ${pkg}:`, err));

        console.log(`Data Safety details saved in ${packageName}.json`);

    } catch (error) {
        console.error(`Error during data recovery for ${packageName}:`, error);
    }
}


import { fileURLToPath } from 'url';
const isMainModule = (metaUrl) => fileURLToPath(metaUrl) === process.argv[1];

if (isMainModule(import.meta.url)) {
    main().catch(error => {
        console.error("Unhandled error in main:", error);
    });
}
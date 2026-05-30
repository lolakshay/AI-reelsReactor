const axios = require("axios");
const cheerio = require("cheerio");

module.exports = snapsave = (targetUrl) => {
    return new Promise(async (resolve) => {
        try {
            // Step 1: Validate the URL
            // Checks if the URL is from a supported platform (Instagram or Facebook)
            const isInstagramUrl = targetUrl.match(/(https|http):\/\/www.instagram.com\/(p|reel|tv|stories)/gi);
            const isFacebookUrl = targetUrl.match(/(?:https?:\/\/(web\.|www\.|m\.)?(facebook|fb)\.(com|watch)\S+)?$/);

            if (!isInstagramUrl && !isFacebookUrl) {
                return resolve({
                    developer: "@Akshay Srinivas", // Changed from Milan Bhandari
                    status: false,
                    msg: "Link Url not valid"
                });
            }

            // Step 2: Make the POST request to the Snapsave API
            const headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://snapsave.app",
                "referer": "https://snapsave.app/id",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            };

            const response = await axios.post(
                "https://snapsave.app/action.php?lang=id",
                'url=' + targetUrl, {
                    headers: headers
                }
            );

            // Step 3: Parse the HTML response to find video links
            const htmlData = response.data;
            const $ = cheerio.load(htmlData);
            const downloadLinks = [];

            // Case 1: The response contains a table of download links
            if ($("table.table").length || $("article.media > figure").length) {
                const thumbnail = $("article.media > figure").find("img").attr("src");
                $("tbody > tr").each((index, element) => {
                    const tableCells = $(element).find('td');
                    const resolution = tableCells.eq(0).text();
                    let downloadUrl = tableCells.eq(2).find('a').attr("href") || tableCells.eq(2).find("button").attr("onclick");

                    // Handle dynamic URLs that require an additional API call
                    const requiresApiCall = /get_progressApi/ig.test(downloadUrl || '');
                    if (requiresApiCall) {
                        downloadUrl = /get_progressApi\('(.*?)'\)/.exec(downloadUrl || '')?.[1] || downloadUrl;
                    }
                    
                    const videoInfo = {
                        resolution: resolution,
                        thumbnail: thumbnail,
                        url: downloadUrl,
                        requiresApiCall: requiresApiCall
                    };
                    downloadLinks.push(videoInfo);
                });
            } 
            // Case 2: The response contains a gallery/thumbnail-style layout
            else if ($("div.download-items__thumb").length) {
                $("div.download-items__thumb").each((index, element) => {
                    const thumbnail = $(element).find("img").attr("src");
                    $("div.download-items__btn").each((btnIndex, btnElement) => {
                        let downloadUrl = $(btnElement).find('a').attr('href');
                        if (!/https?:\/\//.test(downloadUrl || '')) {
                            downloadUrl = "https://snapsave.app" + downloadUrl;
                        }
                        const videoInfo = {
                            thumbnail: thumbnail,
                            url: downloadUrl
                        };
                        downloadLinks.push(videoInfo);
                    });
                });
            }

            // Step 4: Handle cases where no links are found
            if (!downloadLinks.length) {
                return resolve({
                    developer: "@Akshay Srinivas", // Changed from Milan Bhandari
                    status: false,
                    msg: "Blank data"
                });
            }

            // Step 5: Return the successful response with video links
            return resolve({
                developer: "@Akshay Srinivas", // Changed from Milan Bhandari
                status: true,
                data: downloadLinks
            });

        } catch (err) {
            // Handle any errors that occur during the process
            return resolve({
                developer: "@Akshay Srinivas", // Changed from Milan Bhandari
                status: false,
                msg: err.message
            });
        }
    });
};
/**
 * When the page is loaded, do some stuff
 */
$(document).ready(function() {
    // Used to draw the correct element type
    elementMap = {
        "Summary" : drawSummary,
        "Table" : drawTable,
        "Gallery" : drawGallery
    };

    // Used to draw the correct page
    contentMap = {
        "index" : drawIndex,
        "verification" : drawVerification,
        "validation" : drawValidation,
        "performance" : drawPerformance,
        "numerics" : drawNumerics
    };

    // Append the generated content
    $('#nav').append(drawNav());
    $('#content').append(contentMap[vvType]());
    $("#tabs").tabs();
});

/**
 * Draw the navigation sidebar
 */
function drawNav() {
    html = "";
    var data = loadJSON(indexPath + '/index.json');
    for (var cat in data["Elements"]) {
        if (data["Elements"][cat] != null && Object.keys(data["Elements"][cat]["Data"]).length > 0) {
            html += "<h3>" + data["Elements"][cat]["Title"] + "</h3>\n";
            testList = Object.keys(data["Elements"][cat]["Data"]).sort();
            for (idx in testList) {
                html += "<a href=" + indexPath + "/" + data["Elements"][cat]["Title"].toLowerCase() + "/" + testList[idx] + ".html>" + testList[idx] + "</p>\n";
            }
        }
    }

    return html;
}

/**
 * Generatees the summary content page
 */
function drawIndex() {
    html = "";
    var data = loadJSON(indexPath + '/index.json');
    for (var cat in data["Elements"]) {
        if (data["Elements"][cat] != null && Object.keys(data["Elements"][cat]["Data"]).length > 0) {
            html += "<h1>" + data["Elements"][cat]["Title"] + "</h1>\n";
            elemType = data["Elements"][cat]["Type"];
            html += elementMap[elemType](data["Elements"][cat]);
        }
    }
    return html;
}


/**
 * Generates the verification content page
 */
function drawVerification() {
    var verType = window.location.href.substr(
            window.location.href.lastIndexOf("/")+1).split("#")[0].replace(".html", "");
    var data = loadJSON('./' + verType + ".json");
    var testCases = Object.keys(data).sort();
    
    // Add the tabs
    html = "<div id=\"tabs\">\n";
    html += "<ul>\n";
    for (var idx in testCases) {
        html += "<li><a href=\"#" + testCases[idx] + "\">" + testCases[idx] + "</a></li>\n";
    }
    html += "</ul>\n";
    
    // Add the content
    for (var idx in testCases) {
        html += "<div id=\"" + testCases[idx] + "\">\n";

        html += "</div>\n";
    }
    
    // End #tabs div
    html += "</div>\n";
    return html;
}


/**
 * Generates the validation content page
 */
function drawValidation() {
    html = "";
    return html;
}


/**
 * Generates the performance content page
 */
function drawPerformance() {
    html = "";
    return html;
}


/**
 * Generates the numerics content page
 */
function drawNumerics() {
    html = "";
    return html;
}


/**
 * Build a table
 */
function drawSummary(data) {
    var tableHTML = "<table>\n";
    // Add the headers
    tableHTML += "<th></th>\n";
    for (var header in data["Headers"]) {
        tableHTML += "<th>" + data["Headers"][header] + "</th>\n";
    }
    

    // Add the data
    var testNames = Object.keys(data["Data"]).sort();
    for (var idx in testNames) {
        testName = testNames[idx];
        tableHTML += "<tr class=\"testName\"><td>" + testName + "</td></tr>\n";
        for (var testCase in data["Data"][testName]) {
            html_tmp1 = "<tr ";
            html_tmp2 = ">\n<td class=\"testCase\">" + testCase + "</td>\n";
            for (var headerIdx in data["Headers"]) {
                header = data["Headers"][headerIdx];
                html_tmp2 += "<td>"; 
                value = data["Data"][testName][testCase][header];
                dtype = typeof value;
                style = "";  
                if (dtype == 'number') {
                    html_tmp2 += value;
                } else if (dtype == 'object') {
                    if (value.length == 2) {
                        html_tmp2 += value[0] + " of " + value[1];
                        // Handle failures
                        if (value[0] != value[1]) {
                            style = "style=\"color:red\"; ";
                        }
                    }
                }
                html_tmp2 += "</td>\n";
            }
            tableHTML += html_tmp1 + style + html_tmp2 + "</tr>\n";
        }
    }
    
    tableHTML += "</table>\n";
    return tableHTML;
}


/**
 * Build a table
 */
function drawTable(data) {
    tableHTML = "";
    return tableHTML;
}


/**
 * Build a gallery
 */
function drawGallery(meta, data) {
    var galleryHTML = "";
    return galleryHTML;
}


/**
 * Load a json file into a variable
 */
function loadJSON(path) {
    var data;
    $.ajax({
        'async': false,
        'global': false,
        'url': path,
        'dataType': "json",
        'success': function(json) {
            data = json;
        }
    });
    return data;
}


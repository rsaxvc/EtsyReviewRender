# EtsyReviewRender
Render reviews.json as JPEG images

# Example Output
Reviews are converted to a CSV file you can import into Microsoft Excel or Google Sheets:
![ReviewCSV](README_Files/output_csv.jpg)


Review-images are rendered to (OrderNumber)_(Reviewer).jpg:
![ReviewFiles](README_Files/output_folder.jpg)

Review-images looks like this:

![Review1](README_Files/1_rsaxvc.jpg)
![Review2](README_Files/2_BummerGuy.jpg)
![Review3](README_Files/3_ExampleReviewer.jpg)

# Tunables

* Specify the width of the output with `--width WIDTH`
* Specify the header-font style and size with `--headerFontSize HEADERFONTSIZE --headerFontTtf HEADERFONT.TTF`
* Specify the body-font style and size with `--bodyFontSize BODYFONTSIZE --bodyFontTtf BODYFONT.TTF`
* Exclude short messages with `--minMsgLen MINMSGLEN`
* Use a custom star-file with `--starFile STARFILE`


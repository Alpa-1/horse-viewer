package main

import (
	"embed"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// go:embed cmd/server/crop.exe
// go:embed all:cmd/server/poppler-23.07.0/Library/bin
// go:embed all:dist/spa
var StaticFiles embed.FS

var logger = log.Default()

func main() {
	logger.Println("Starting server on port 8080")

	r := gin.Default()

  r.Use(static.Serve("/", static.LocalFile("./dist/spa", true)))

	r.OPTIONS("/fetch", func(c *gin.Context){
		c.Header("Access-Control-Allow-Origin", "http://localhost:9000")
		c.Header("Access-Control-Allow-Methods", "OPTIONS, POST")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Access-Control-Allow-Origin")

		c.AbortWithStatus(204)
	})

	r.POST("/fetch", func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "http://localhost:9000")
		c.Header("Access-Control-Allow-Methods", "OPTIONS, POST")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Access-Control-Allow-Origin")

		b, err := ioutil.ReadAll(c.Request.Body)
		if err != nil {
			logger.Println("Error: ", err.Error())
			return
		}
		imageData := crop(string(b))
		if imageData == nil {
			c.AbortWithStatus(500)
			return
		}
		c.Header("Content-Type", "image/jpeg")
    	c.Header("Content-Length", strconv.Itoa(len(imageData)))
		c.Writer.WriteHeader(http.StatusOK)
		c.Writer.Write(imageData)
		})
	r.Run()

}

func crop(url string) []byte{
	b := get(url)
	if b == nil {
		logger.Println("Error: ", "Could not get PDF")
		return nil
	}
	id, err := uuid.NewUUID()
	if err != nil {
		logger.Println("Error: ", "Could not generate UUID")
		return nil
	}

	var tempfileName string = "temp-"+id.String()+".pdf"
	var tempImageName string = "output_image-" + id.String() + ".png"
	err = os.WriteFile(tempfileName, b, 0644)
	if err != nil {
		logger.Println("Error: ", "Could not save PDF")
		return nil
	}
	logger.Println("Saved PDF")
	defer os.Remove(tempfileName)

	cwd, err := os.Getwd()
	if err != nil {
		logger.Println("Error: ", "Could not get working directory")
		return nil
	}

	cmd := exec.Command(filepath.Join(cwd, "crop.exe"), tempfileName, tempImageName)
	err = cmd.Run()
	if err != nil {
		logger.Println("Error: ", "Could not crop PDF")
		logger.Println(err.Error())
		return nil
	}

	readImage, err := ioutil.ReadFile(tempImageName)
	if err != nil {
		logger.Println("Error: ", "Could not read image")
		return nil
	}
	defer os.Remove(tempImageName)

	return readImage
}

func get(url string) []byte{
	resp, err := http.Get(url)
	if err != nil {
		logger.Println(err.Error())
		return nil
	}
	logger.Println(resp)
	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		logger.Println(err.Error())
		return nil
	}

	return b
}
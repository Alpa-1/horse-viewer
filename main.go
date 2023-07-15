package main

import (
	"embed"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"syscall"
	"unsafe"

	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// go:embed crop
// go:embed all:cmd/server/poppler-23.07.0/Library/bin
// go:embed all:dist/spa
var StaticFiles embed.FS
var filePayload []byte


func main() {
  fd, err := memfdCreate("./crop")
  if err != nil {
      log.Println(err.Error())
  }

  err = copyToMem(fd, filePayload)
  if err != nil {
      log.Println(err.Error())
  }

  log.SetOutput(os.Stdout)

  log.Println("Starting server")

	r := gin.Default()
  port := os.Getenv("PORT")
  if port == "" {
    port = "8080"
  }
  r.Use(static.Serve("/", static.LocalFile("./dist/spa", true)))

	r.OPTIONS("/fetch", func(c *gin.Context){
		// c.Header("Access-Control-Allow-Origin", "http://localhost:9000")
		c.Header("Access-Control-Allow-Origin", "https://horse-viewer-3405d82093da.herokuapp.com")
		c.Header("Access-Control-Allow-Methods", "OPTIONS, POST")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Access-Control-Allow-Origin")

		c.AbortWithStatus(204)
	})

	r.POST("/fetch", func(c *gin.Context) {
		// c.Header("Access-Control-Allow-Origin", "http://localhost:9000")
		c.Header("Access-Control-Allow-Origin", "https://horse-viewer-3405d82093da.herokuapp.com")
		c.Header("Access-Control-Allow-Methods", "OPTIONS, POST")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Access-Control-Allow-Origin")

		b, err := ioutil.ReadAll(c.Request.Body)
		if err != nil {
			log.Println("Error: ", err.Error())
      c.AbortWithStatus(500)
		}
		imageData := crop(string(b), fd)
		if imageData == nil {
      log.Println("Error: ", "Could not crop PDF")
			c.AbortWithStatus(500)
		}
		c.Header("Content-Type", "image/jpeg")
    	c.Header("Content-Length", strconv.Itoa(len(imageData)))
		c.Writer.WriteHeader(http.StatusOK)
		c.Writer.Write(imageData)
		})
	r.Run(":"+port)

}

func crop(url string, fd uintptr) []byte{
	b := get(url)
	if b == nil {
		log.Println("Error: ", "Could not get PDF")
		return nil
	}
	id, err := uuid.NewUUID()
	if err != nil {
		log.Println("Error: ", "Could not generate UUID")
		return nil
	}

	var tempfileName string = "temp-"+id.String()+".pdf"
	var tempImageName string = "output_image-" + id.String() + ".png"
	err = os.WriteFile(tempfileName, b, 0644)
	if err != nil {
		log.Println("Error: ", "Could not save PDF")
		return nil
	}
	log.Println("Saved PDF")
	defer os.Remove(tempfileName)

	// cwd, err := os.Getwd()
	// if err != nil {
	// 	log.Println("Error: ", "Could not get working directory")
	// 	return nil
	// }

  err = execveAt(fd, []string{tempfileName, tempImageName})
  if err != nil {
    log.Println("Error: ", "Could not crop PDF")
    log.Println(err.Error())
    return nil
  }

	// cmd := exec.Command(filepath.Join(cwd, "./crop"), tempfileName, tempImageName)
	// err = cmd.Run()
	if err != nil {
		log.Println("Error: ", "Could not crop PDF")
		log.Println(err.Error())
		return nil
	}

	readImage, err := ioutil.ReadFile(tempImageName)
	if err != nil {
		log.Println("Error: ", "Could not read image")
		return nil
	}
	defer os.Remove(tempImageName)

	return readImage
}

func get(url string) []byte{
	resp, err := http.Get(url)
	if err != nil {
		log.Println(err.Error())
		return nil
	}
	log.Println(resp)
	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println(err.Error())
		return nil
	}

	return b
}

func memfdCreate(path string) (r1 uintptr, err error) {
    s, err := syscall.BytePtrFromString(path)
    if err != nil {
        return 0, err
    }

    r1, _, errno := syscall.SyscallN(319, uintptr(unsafe.Pointer(s)), 0, 0)

    if int(r1) == -1 {
        return r1, errno
    }

    return r1, nil
}

func copyToMem(fd uintptr, buf []byte) (err error) {
  _, err = syscall.Write(int(fd), buf)
  if err != nil {
      return err
  }

  return nil
}

func execveAt(fd uintptr, argv []string ) (err error) {
  s, err := syscall.BytePtrFromString("")
  if err != nil {
      return err
  }
  ss, err := syscall.SlicePtrFromStrings(argv)
  if err != nil{
    return err
  }

  ret, _, errno := syscall.SyscallN(322, fd, uintptr(unsafe.Pointer(s)), uintptr(unsafe.Pointer(&ss[0])), 0, 0x1000, 0)
  if int(ret) == -1 {
      return errno
  }

  // never hit
  log.Println("should never hit")
  return err
}

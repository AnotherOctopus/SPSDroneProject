package main

import (
        "net/http"
        "log"
        "fmt"
	"math/rand"
	"time"
        "io/ioutil"
        "os"
)


const prospectdir = "./prospective"
const persondir = "./person"
const backdir = "./notperson"

func postresp(w http.ResponseWriter, r * http.Request) {
        bdy := make([]byte,r.ContentLength)
        r.Body.Read(bdy)
        fmt.Println(string(bdy))
        srcimg := fmt.Sprintf("%v/%v",prospectdir,string(bdy[:r.ContentLength-2]))
        dstimg := fmt.Sprintf("%v/%v",backdir,string(bdy[:r.ContentLength-2]))
        if bdy[r.ContentLength-1] == '1'{
                dstimg = fmt.Sprintf("%v/%v",persondir,string(bdy[:r.ContentLength-2]))
        }
        fmt.Println(fmt.Sprintf("mv %v to %v",srcimg,dstimg))
        err := os.Rename(srcimg,dstimg)
        fmt.Println(time.Now())
        fmt.Println(err)
        fmt.Println(err)
        w.Write([]byte("recv"))
}
func selectImg(imgdir string) string{
    files, err := ioutil.ReadDir(imgdir)
    if err != nil {
        log.Fatal(err)
    }

    for _, f := range files {
            fmt.Println(f.Name())
            return f.Name()
    }
    return ""
}
func imgresp(w http.ResponseWriter, r * http.Request) {
        imgname := selectImg(prospectdir)
        cookie1 := &http.Cookie{Name: "imgname", Value: imgname, HttpOnly: false}
        http.SetCookie(w, cookie1)
        w.Header().Set("Cache-Control","no-cache, no-store, must-revalidate")
        w.Header().Set("Pragma","no-cache")
        w.Header().Set("Expires","0")
        http.ServeFile(w, r, fmt.Sprintf("%v/%v",prospectdir,imgname))
}

func main() {
	rand.Seed(time.Now().UTC().UnixNano())
        http.Handle("/", http.FileServer(http.Dir("./static")))
        http.Handle("/post", http.HandlerFunc(postresp))
        http.Handle("/frame.jpg", http.HandlerFunc(imgresp))
        http.ListenAndServe(":80", nil)
}

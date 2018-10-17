package main

import (
        "net/http"
        "log"
	"hash/fnv"
        "os"
        "fmt"
        "gopkg.in/mgo.v2"
        "bytes"
        "gopkg.in/mgo.v2/bson"
        "strconv"
	"math/rand"
	"time"
)

type BB struct {
    ID int
    w []float64
    h []float64
    Xpos []float64
    Ypos []float64
}
const imgdir = "/media/cephalopodoverlord/CHARLES/dronevid/yolo/darknet/data/dronedata/rawset2"
const numframes = 6835
func parseToJson(body []byte)( *BB) {
    bb := new(BB)
    tr := bytes.Trim(body,"\x00")
    sp := bytes.Split(tr, []byte("&"))
    for _,by := range sp{
        chunks := bytes.Split(by,[]byte("="))
        key := string(chunks[0])
        if  key == "ID"{
                bb.ID ,_ = strconv.Atoi(string(chunks[1]))
        } else if key == "Xpos"{
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.Xpos = append(bb.Xpos,xf)
                }
        } else if key == "Ypos"{
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.Ypos = append(bb.Ypos,xf)
                }
        } else if key == "widths" {
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.w = append(bb.w,xf)
                }
        } else if key == "heights" {
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.h = append(bb.h,xf)
                }
        } else {
                panic("NO KEY")
        }
    }
    return bb
}
func postresp(w http.ResponseWriter, r * http.Request) {
        bdy := make([]byte,10000)
        r.Body.Read(bdy)
        taggedData := parseToJson(bdy)

        session, _ := mgo.Dial("localhost")
        defer session.Close()
        session.SetMode(mgo.Monotonic, true)
        c := session.DB("DroneTagsLight").C("people")

        exist := new(BB)
        //c.Update(bson.M{"id":taggedData.ID},taggedData)
        change := mgo.Change{
                Update: bson.M{"$set": bson.M{"id":taggedData.ID,"xpos":taggedData.Xpos,"ypos":taggedData.Ypos,"h":taggedData.h,"w":taggedData.w}},
                Upsert: true,
                ReturnNew: true,
        }
        c.Find(bson.M{"id":taggedData.ID}).Apply(change,exist)
        log.Printf("%v;%v;\n",r.RemoteAddr,len(taggedData.h))
        http.ServeFile(w, r, "./static/thanks.html")
}
func randomImg()(id int, imagename string){
	imgchunkvals := []int{0,608,1216,1824,2432,3040}
	framenum := rand.Intn(numframes)
	xval := imgchunkvals[rand.Intn(len(imgchunkvals))]
	yval := imgchunkvals[rand.Intn(len(imgchunkvals))]
	filename := fmt.Sprintf("frame%v/%v-%v.png",framenum,xval,yval)
	h := fnv.New32a()
	h.Write([]byte(filename))
	return int(h.Sum32()), filename
}
func selectImg(dirname string)(ID string) {
        session, _ := mgo.Dial("localhost")
        defer session.Close()
        c := session.DB("DroneTagsLight").C("people")
        exist := new(BB)
	imgid,imgname := randomImg()
        found := c.Find(bson.M{"id":imgid}).One(exist)
        _, err := os.Stat(fmt.Sprintf("%v/%v",dirname,imgname));
        for  err != nil || found == nil{
		imgid,imgname = randomImg()
		found = c.Find(bson.M{"id":imgid}).One(exist)
		_, err = os.Stat(fmt.Sprintf("%v/%v",dirname,imgname));
        }
        return imgname
}
func imgresp(w http.ResponseWriter, r * http.Request) {
        imgname := selectImg(imgdir)
        cookie1 := &http.Cookie{Name: "ID", Value: imgname, HttpOnly: false}
        http.SetCookie(w, cookie1)
        w.Header().Set("Cache-Control","no-cache, no-store, must-revalidate")
        w.Header().Set("Pragma","no-cache")
        w.Header().Set("Expires","0")
        http.ServeFile(w, r, fmt.Sprintf("%v/%v",imgdir,imgname))
}

func main() {
	rand.Seed(time.Now().UTC().UnixNano())
        http.Handle("/", http.FileServer(http.Dir("./static")))
        http.Handle("/return", http.HandlerFunc(postresp))
        http.Handle("/frame.jpg", http.HandlerFunc(imgresp))
        http.ListenAndServe(":80", nil)
}

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"time"

	"github.com/fsnotify/fsnotify"
)

type Config struct {
	ShutdownTime string `json:"shutdown_time"`
	Timer        *time.Timer
}

func (c *Config) SetTimer() {
	if c.ShutdownTime == "" {
		log.Println("no shutdown time, not set timer")
		return
	}
	now := time.Now()
	shutdownTime := fmt.Sprintf("%v %v", now.Format("2006-01-02"), c.ShutdownTime)
	t, err := time.ParseInLocation("2006-01-02 15:04:05", shutdownTime, time.Local)
	if err != nil {
		log.Printf("parse shutdown time error: %v\n", err)
		return
	}
	timeStr := now.Format("15:04:05")
	if timeStr >= c.ShutdownTime {
		log.Println("now already over shutdown time, so shutdown next day")
		t = t.Add(time.Hour * 24)
	}
	log.Println("set timer at ", t)

	if c.Timer == nil {
		c.Timer = time.AfterFunc(t.Sub(now), Shutdown)
	} else {
		c.Timer.Reset(t.Sub(now))
	}
}

func (c Config) String() string {
	return fmt.Sprintf("Config: shutdown time is %v", c.ShutdownTime)
}

func (c *Config) Equal(other *Config) bool {
	return c.ShutdownTime == other.ShutdownTime
}

func readConfig(file string) (*Config, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	var c Config
	if err := json.NewDecoder(f).Decode(&c); err != nil {
		if errors.Is(err, io.EOF) {
			return &Config{}, nil
		}
		return nil, err
	}
	return &c, nil
}

func Shutdown() {
	fmt.Println("shutdown!!!!")
	cmd := exec.Command("shutdown", "-s", "-t", "10")
	d, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Shutdown error: %v\n", err)
		return
	}
	log.Println(d)
}

func main() {
	if len(os.Args) < 2 {
		log.Fatalln("Please support a config file.")
	}
	file := os.Args[1]
	config, err := readConfig(file)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(config)
	config.SetTimer()

	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	done := make(chan bool)
	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				log.Println("event:", event)
				if event.Op&fsnotify.Write == fsnotify.Write {
					log.Println("modified file:", event.Name)
					newConfig, err := readConfig(file)
					if err != nil {
						log.Printf("read config file error: %v\n", err)
					}
					if config.Equal(newConfig) {
						log.Println("new config same with old config!")
					} else {
						log.Println("new", newConfig)
						log.Println("old", config)
						config.ShutdownTime = newConfig.ShutdownTime
						config.SetTimer()
					}
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				log.Println("watcher error:", err)
			}
		}
	}()

	err = watcher.Add(file)
	if err != nil {
		log.Fatal(err)
	}
	<-done

}


(require '[babashka.fs :as fs]
         '[clojure.tools.cli :refer [parse-opts]]
         )
(defn drives [] (vec (java.io.File/listRoots)))
(defn is-orboboot? [f]
  (not (empty? (filter #(= (fs/extension %) "UF2") (fs/list-dir f))))
  )
(defn orboboot-drive[]
  (first (filter is-orboboot? (drives))))

(defn wait-for-orboboot []
  (println "waiting for orboboot")
  (while (nil? (orboboot-drive))
    (Thread/sleep 100))
  (orboboot-drive))

(defn is-circuitpy? [f]
  (not (empty? (filter
                #(and (= (fs/file-name %) "lib")
                     (fs/directory? %)) (fs/list-dir f)
                ))))

(defn circuitpy-drive []
  (first (filter is-circuitpy? (drives))))

(defn wait-for-circuitpy []
  (println "Waiting for circuitpy")
  (while (nil? (circuitpy-drive))
    (Thread/sleep 100))
  (circuitpy-drive))

(defn copy-firmware [src dest]
  (println "Copying firmware from " src " to " dest)
  (fs/copy src dest)
  )

(defn program-firmware [firmware-filename]
  (let [orboboot-drive (wait-for-orboboot)]
    (copy-firmware (fs/file firmware-filename) orboboot-drive)))

(defn copy-program [src dest]
  (println "deleting dest items")
  (fs/delete-tree (clojure.string/join [dest "lib"]))
  (fs/delete-if-exists (clojure.string/join [dest "code.py"]))
  (println "Copying lib from " src " to " dest)
  (fs/create-dir (clojure.string/join [dest "lib"]))
  (fs/copy-tree (clojure.string/join fs/file-separator [src "lib"])
                (clojure.string/join fs/file-separator [dest "lib"]))
  (println "Copying code.py from " src " to " dest)
  (fs/copy (clojure.string/join fs/file-separator [src "code.py"]) dest))

(defn program-program [f]
  (let [circuitpy-drive (wait-for-circuitpy)]
    (copy-program f circuitpy-drive)))

(def default-firmware "orbotron_v4_20210209_qtpy.uf2")
(def default-program "programs/basic_joystick")

(defn program-orbotron [firmware-filename program-directory]
  (program-firmware firmware-filename)
  (program-program program-directory))

(def cli-options
  [["-f" "--firmware FIRMWARE-FILE" "Firmware file (uf2)"
    :default default-firmware ]
   ["-p" "--program PROGRAM-PATH" "Source path of code"
    :default default-program]
   ["-l" "--loop"]])

(let [options (:options (parse-opts *command-line-args* cli-options))]
                                        ;(println options)
  (loop []
    (program-orbotron (:firmware options) (:program options))
    (println "\n\n")
    (if (:loop options)
      (recur)
      nil))
  )

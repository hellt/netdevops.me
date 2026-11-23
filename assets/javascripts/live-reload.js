// Zensical's own reload client checks the initially loaded path, which becomes
// stale after instant navigation. Follow the current path in the preview only.
(() => {
  const url = new URL(window.location.href)
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:"
  url.hash = ""
  let closed = false

  function connect() {
    const socket = new WebSocket(url.href)
    socket.addEventListener("message", event => {
      if (event.data === window.location.pathname) {
        window.location.reload()
      }
    })
    socket.addEventListener("open", () => {
      if (closed) {
        window.location.reload()
      }
    })
    socket.addEventListener("close", () => {
      closed = true
      setTimeout(connect, 1000)
    })
  }

  connect()
})()

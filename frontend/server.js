const express = require('express');
const path = require('path');

const app = express();

// 托管 Angular 构建后的静态文件
const distPath = path.join(__dirname, 'dist/cloud-media-platform');
app.use(express.static(distPath));

// 所有路由都返回 index.html（支持 Angular 路由）
app.get('/*', (req, res) => {
  res.sendFile(path.join(distPath, 'index.html'));
});

// 从环境变量读取端口，Azure 会自动设置 PORT
const port = process.env.PORT || 8080;

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

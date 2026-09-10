// Exercise the shipped browser worker, not just the presence of search.json.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

async function main() {
  const index = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const messages = [];
  const self = { postMessage: message => messages.push(message) };
  vm.runInNewContext(fs.readFileSync(process.argv[3], 'utf8'), { self });

  await self.onmessage({ data: { type: 0, data: index } });
  assert.equal(messages.pop().type, 1, 'Search worker must initialize');

  for (const query of ['orbstack', 'gnmic']) {
    await self.onmessage({ data: { type: 2, data: {
      input: query,
      filter: {
        input: { type: 'operator', data: { operator: 'and', operands: [] } },
        aggregation: { input: [] },
      },
    } } });
    const result = messages.pop();
    assert.equal(result.type, 3);
    assert.ok(result.data.items.some(item => {
      const page = index.items[item.id];
      return page.location.includes(query) && /^\d{4}\//.test(page.location);
    }), `Search for ${query} must find a blog post`);
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

"""S06: verifica en navegador que un mensaje HTML no ejecuta código en Aula Nova."""
import os,json
from playwright.sync_api import sync_playwright,expect

def test_aula_s06_html_inyectado_se_muestra_como_texto():
    base=os.environ.get('AULA_BASE_URL','http://aula-nova:3000')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page()
        payload='<img src=x onerror="window.__s06_executed=1">'
        response=page.request.post(base+'/api/messages',data=json.dumps({'courseId':'calc-201','subject':'Control S06','body':payload}),headers={'Content-Type':'application/json'})
        # El cliente JSON de Playwright necesita data=string para Content-Type application/json.
        # Si el servidor no acepta el JSON, no registrar un aprobado artificial.
        assert response.status==201, response.text()
        page.goto(base+'/#mensajes')
        expect(page.locator('.message-entry').filter(has_text='Control S06')).to_contain_text(payload)
        assert page.evaluate('window.__s06_executed||0')==0
        browser.close()

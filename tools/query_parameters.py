import click

def queryParameters(cal_id):
    return """select 
        nombre || ': '::text || valor::text 
    from cal_pars 
    join parametros on 
        (cal_pars.model_id=parametros.model_id and cal_pars.orden=parametros.orden) 
    where cal_id={cal_id} 
    order by cal_pars.orden""".format(cal_id=cal_id)

@click.command()
@click.argument('cal_id', type=int)
def comm(cal_id):
    print(queryParameters(cal_id))

if __name__ == '__main__':
    comm()

